import os.path
import shutil
import tempfile
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, Form, Depends, File, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import create_db_and_tables, get_async_session, Post, User
from app.images import imagekit
from app.schemas_user import UserRead, UserCreate, UserUpdate
from app.user import auth_backend, fastapi_users, current_active_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# Registration
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Email verification
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

# Password reset
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        caption: str = Form(""),
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    """
    Upload an image to ImageKit and save metadata to the database.

    Steps:
    1. Validate the file is an image
    2. Save to a temporary file (ImageKit SDK needs a file path)
    3. Upload to ImageKit cloud storage
    4. Save the post-metadata to our database
    5. Clean up the temporary file
    """

    # Step 1: Validate a file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )

    temp_file_path = None

    try:
        # Step 2: Save an uploaded file to a temporary location
        # We need this because ImageKit SDK requires a file path or file object
        file_extension = os.path.splitext(file.filename)[1]  # e.g., ".jpg"

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file_path = temp_file.name
            # Copy the uploaded file content to our temp file
            shutil.copyfileobj(file.file, temp_file)

        # Step 3: Upload to ImageKit
        with open(temp_file_path, 'rb') as image_file:
            upload_result = imagekit.files.upload(
                file=image_file,
                file_name=file.filename,

                tags="backend-upload",
                folder="/uploads"

            )

        # Step 4: Get the uploaded image URL from ImageKit response
        # The response contains the CDN URL where the image is now hosted
        image_url = upload_result.url
        # Step 5: Save post-metadata to a database
        post = Post(
            user_id=user.id,
            caption=caption,
            url=image_url,
            file_type=file.content_type,
            file_name=file.filename,
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)

        return {
            "message": "Upload successful",
            "post_id": str(post.id),
            "image_url": image_url,
            "caption": caption
        }

    except Exception as e:
        # Log the error for debugging
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    finally:
        # Step 6: Always clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.get("/feed")
async def get_feed(session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]
    post_data = []
    for post in posts:
        post_data.append(
            {
                "id": str(post.id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "user_id": str(post.user_id),
                "user": post.user
            }
        )
    return {"posts": post_data}


@app.get("/posts/{post_id}")
async def get_post(post_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).filter(Post.id == post_uuid))
        post = result.scalars().first()
        if not post:
            raise HTTPException(status_code=404, detail=f"Post not found: {post_id}")
        return post
    except Exception as e:
        print(f"Error getting post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting post: {str(e)}")


@app.delete("/delete/{post_id}")
async def delete_post(
        post_id: str,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).filter(Post.id == post_uuid))
        post = result.scalars().first()
        if not post:
            raise HTTPException(status_code=404, detail=f"Post not found: {post_id}")

        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this post")

        await session.delete(post)
        await session.commit()
        return {"message": "Post deleted successfully"}

    except Exception as e:
        print(f"Error deleting post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting post: {str(e)}")


@app.get("/me/feed")
async def my_feed(session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)):
    result = await session.execute(select(Post).where(Post.user_id == user.id).order_by(Post.created_at.desc()))
    posts = result.scalars().all()
    return {"posts": [{
        "id": str(p.id),
        "caption": p.caption,
        "url": p.url,
        "file_type": p.file_type,
        "file_name": p.file_name,
        "created_at": p.created_at.isoformat(),
    } for p in posts]}
