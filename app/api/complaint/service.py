from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, UploadFile, HTTPException, status
from sqlalchemy import select, func
from pydantic import UUID4
from datetime import datetime
from typing import List

from app.database import db_session
from app.models import Complaint
from app.schemas import CreateComplaint, UpdateComplaint
from app.common.http_response_model import PageMeta
from pathlib import Path
import os
import aiofiles
import uuid
from app.common.utils import sanitize_string


class ComplaintService:
    def __init__(self, session: AsyncSession = Depends(db_session)) -> None:
        self.session = session

    # get all complaints
    async def get_all_complaints(self, page: int, page_size: int) -> list[Complaint]:
        collections_to_skip = (page - 1) * page_size

        # Get total number of items
        total_items = await self.session.execute(select(func.count()).select_from(Complaint))
        total_items = total_items.scalar()

        # Calculate total pages
        total_pages = -(-total_items // page_size)

        # Fetch paginated items
        collection_list = await self.session.execute(
            select(Complaint)
            .offset(collections_to_skip)
            .order_by(Complaint.updated_at.desc())
            .limit(page_size)
        )
        collections = collection_list.scalars().fetchall()

        return collections, PageMeta(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_items=total_items
        )

    # get an complaints by id
    async def get_complaint_by_id(self, id: UUID4) -> Complaint:
        collection_record = await self.session.execute(select(Complaint).where(Complaint.id == id))
        collection = collection_record.scalar_one_or_none()

        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

        return collection

    # create a collection
    async def create_complaint(self, data: CreateComplaint) -> Complaint:
        complaint = Complaint(**data.dict())
        self.session.add(complaint)
        await self.session.commit()
        await self.session.refresh(complaint)

        return complaint

    # update the complaint
    async def update_complaint(
        self, id: UUID4,
        data: UpdateComplaint,
    ) -> Complaint:
        complaint_record = await self.session.execute(select(Complaint).where(Complaint.id == id))
        complaint = complaint_record.scalar_one_or_none()

        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

        # Step 1: Explicitly update the updated_at field
        complaint.updated_at = datetime.utcnow()

        # Step 2: Update the fields with new values
        for field, value in data.dict().items():
            if value is not None:  # Only update if the field was provided in the request
                setattr(complaint, field, value)

        # Step 3: Commit the changes
        self.session.add(complaint)
        await self.session.commit()

        return complaint

    @staticmethod
    async def save_upload_file(upload_file: UploadFile, destination: Path) -> str:
        try:
            async with aiofiles.open(destination, 'wb') as out_file:
                # Read chunks of 1MB
                while content := await upload_file.read(1024*1024):
                    await out_file.write(content)
            return str(destination)
        finally:
            await upload_file.close()

    async def get_uploaded_file_path(self, images: List[UploadFile]) -> List[str]:
        UPLOAD_DIRECTORY = "storage/images"
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
        image_paths = []

        if images:
            for image in images:
                file_name = f"{uuid.uuid4()}-{image.filename}"
                clean_file_name = sanitize_string(file_name)
                file_path = Path(UPLOAD_DIRECTORY) / clean_file_name

                # Calling the static method correctly
                image_path = await ComplaintService.save_upload_file(image, file_path)
                image_paths.append(image_path)

        return image_paths

    # delete the complaint
    # async def delete_collection(self, id: UUID4) -> bool:
    #     collection_record = await self.session.execute(select(Collection).where(Collection.id == id))
    #     collection = collection_record.scalar_one_or_none()

    #     if not collection:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    #     # delete all the tracks of the collection
    #     tracks_records = await self.session.execute(
    #         select(Track)
    #         .where(Track.collection_id == id)
    #     )
    #     tracks = tracks_records.scalars().fetchall()
    #     for track in tracks:
    #         await self.session.delete(track)

    #     # delete the collection
    #     await self.session.delete(collection)
    #     await self.session.commit()

    #     return True

    #     # Get total number of items
    #     tracks_records = await self.session.execute(
    #         select(Track)
    #         # Add this line to join
    #         .join(Collection, Collection.id == Track.collection_id)
    #         .where(Collection.id == collection_id)
    #         .order_by(Track.order_seq.asc())
    #     )
    #     tracks = tracks_records.scalars().fetchall()

    #     return tracks
