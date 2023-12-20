from fastapi import APIRouter, Depends, status, Query, Path, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import UUID4

from app.common.http_response_model import CommonResponse
from app.database import db_session
from app.api.complaint.service import ComplaintService
from app.models import Complaint
from app.schemas import CreateComplaint, UpdateComplaint
router = APIRouter()


@router.get("", name="Get all complaints")
async def get_collections(
        response: Response,
        page: int = Query(1, ge=1),
        per_page: int =
        Query(100, ge=0),
        session: AsyncSession = Depends(db_session)):

    try:
        complaint_service = ComplaintService(session)
        complaints, page_meta = await complaint_service.get_all_complaints(page, per_page)
        payload = CommonResponse[List[Complaint]](
            message="Successfully fetched complaints",
            success=True,
            payload=complaints,
            meta=page_meta
        )
        response.status_code = status.HTTP_200_OK
        return payload

    except HTTPException as http_err:
        payload = CommonResponse(
            success=False,
            message=str(http_err.detail),
            payload=None
        )
        response.status_code = http_err.status_code
        return payload

    except Exception as e:
        payload = CommonResponse(
            success=False,
            message=str(e),
            payload=None
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return payload


@router.get("/{complaint_id}", name="Get complaint by id")
async def get_complaint_by_id(
    response: Response,
    complaint_id: UUID4 = Path(...,
                               title="The ID of the complaint to fetch"),
    session: AsyncSession = Depends(db_session)
):

    try:
        complaint_service = ComplaintService(session)
        complaint = await complaint_service.get_complaint_by_id(complaint_id)

        payload = CommonResponse(
            success=True,
            message="Complaint fetched successfully",
            payload=complaint

        )
        response.status_code = status.HTTP_200_OK
        return payload

    except HTTPException as http_err:
        payload = CommonResponse(
            success=False,
            message=str(http_err.detail),
            payload=None
        )
        response.status_code = http_err.status_code
        return payload

    except Exception as e:
        payload = CommonResponse(
            success=False,
            message=str(e),
            payload=None
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return payload


@router.post("", name="Create a complaint")
async def create_collection(
        response: Response,
        images: Optional[List[UploadFile]] = File(
            None, title="Complaint images"),
        description: str = Form(..., title="The complaint description"),
        user_id: UUID4 = Form(...,
                              title="The ID of the user who created the complaint"),
        category: str = Form(..., title="The complaint category"),
        place: str = Form(..., title="The complaint place"),
        session: AsyncSession = Depends(db_session)):

    try:

        complaint_service = ComplaintService(session)
        uploaded_images_path = await complaint_service.get_uploaded_file_path(
            images=images)

        if uploaded_images_path:
            images_string = ', '.join(uploaded_images_path)
        else:
            images_string = None

        complaint_data = CreateComplaint(
            description=description,
            user_id=user_id,
            category=category,
            place=place,
            images=images_string
        )

        complaint = await complaint_service.create_complaint(complaint_data)
        payload = CommonResponse(
            success=True,
            message="Complaint created successfully",
            payload=complaint
        )
        response.status_code = status.HTTP_201_CREATED
        return payload

    except HTTPException as http_err:
        payload = CommonResponse(
            success=False,
            message=str(http_err.detail),
            payload=None
        )
        response.status_code = http_err.status_code
        return payload

    except Exception as e:
        payload = CommonResponse(
            success=False,
            message="Error creating complaint",
            payload=str(e)
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return payload


@router.patch("/{complaint_id}", name="Update a complaint")
async def update_collection(
    response: Response,
    complaint_id: UUID4 = Path(...,
                               title="The ID of the complaint to update"),
    images: Optional[List[UploadFile]] = File(
        None, title="Complaint images"),
    description: str = Form(None, title="The complaint description"),
    category: str = Form(None, title="The complaint category"),
    place: str = Form(None, title="The complaint place"),
    session: AsyncSession = Depends(db_session)
):

    try:

        complaint_service = ComplaintService(session)
        uploaded_images_path = await complaint_service.get_uploaded_file_path(
            images=images)

        if uploaded_images_path:
            images_string = ', '.join(uploaded_images_path)
        else:
            images_string = None

        complaint_data = UpdateComplaint(
            description=description,
            category=category,
            place=place,
            images=images_string
        )

        updated_collection = await complaint_service.update_complaint(complaint_id, complaint_data)
        payload = CommonResponse(
            success=True,
            message="Collection updated successfully",
            payload=updated_collection
        )
        response.status_code = status.HTTP_200_OK
        return payload

    except HTTPException as http_err:
        payload = CommonResponse(
            success=False,
            message=str(http_err.detail),
            payload=None
        )
        response.status_code = http_err.status_code
        return payload

    except Exception as e:
        payload = CommonResponse(
            success=False,
            message="Error creating album",
            payload=str(e)
        )
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return payload


# @router.delete("/{collection_id}", name="Delete collection")
# async def delete_collection(
#     response: Response,
#     collection_id: UUID4 = Path(...,
#                                 title="The ID of the collection to delete"),
#     session: AsyncSession = Depends(db_session)
# ):

#     try:

#         collection_service = CollectionService(session)
#         await collection_service.delete_collection(collection_id)
#         payload = CommonResponse(
#             success=True,
#             message="Collection deleted successfully",
#             payload=None

#         )
#         response.status_code = status.HTTP_200_OK
#         return payload

#     except HTTPException as http_err:
#         payload = CommonResponse(
#             success=False,
#             message=str(http_err.detail),
#             payload=None
#         )
#         response.status_code = http_err.status_code
#         return payload

#     except Exception as e:
#         payload = CommonResponse(
#             success=False,
#             message="Error creating album",
#             payload=str(e)
#         )
#         response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
#         return payload
