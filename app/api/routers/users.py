from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Annotated, List

from app.api.dependencies.auth import validate_is_authenticated, validate_password_reset
from app.api.dependencies.user import CurrentUserDep, CurrentAdminDep
from app.api.dependencies.core import DBSessionDep
from app.crud.log import create_log
from app.crud.user import (update_user_profile, create_password_token, create_new_password, deposit_for_user,
                           transfer_users, withdraw_user, deposit_user, withdraw_for_user, transfer_for_users)

from app.schemas.user import (User, AuthorizedUser, AuthorizedUserWithBalance, UpdateProfile, ResetPasswordArgs,
                              DepositForUser, DepositResult, WithdrawResult, TransferResult, TransferForUser,
                              DepositUser, WithdrawUser, WithdrawForUser, TransferUser)

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)


@router.get(
    "/me",
    response_model=AuthorizedUser
)
async def user_details(current_user: CurrentUserDep, db_session: DBSessionDep):
    await create_log(db_session, "me", current_user)
    return current_user


@router.patch(
    "/change/profile",
    response_model=AuthorizedUser
)
async def change_profile(
        profile_update: UpdateProfile,
        current_user: CurrentUserDep,
        db_session: DBSessionDep
):
    print(profile_update)
    try:
        updated_user = await update_user_profile(db_session, current_user, profile_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    await create_log(db_session, "change_profile", current_user)
    return updated_user


@router.post(
    "/make/password_reset_token"
)
async def make_password_reset_token(
        current_user: CurrentUserDep,
        db_session: DBSessionDep
):
    user = await create_password_token(db_session, current_user)
    await create_log(db_session, "make_password_reset_token", current_user)
    return "Create success new password token"


@router.post(
    "/reset_password",
)
async def reset_password(
        reset_password_args: ResetPasswordArgs,
        db_session: DBSessionDep,
        current_user: User = Depends(validate_password_reset),
):
    user = await create_new_password(db_session, current_user, reset_password_args)

    await create_log(db_session, "reset_password", current_user)

    return {"Success": True}


@router.get(
    "/admin",
    response_model=AuthorizedUser
)
async def user_details(current_admin: CurrentAdminDep):
    return current_admin



@router.post(
    "/deposit/me",
    response_model=DepositResult
)
async def deposit_me(
        deposit: DepositUser,
        current_user: CurrentUserDep,
        db_session: DBSessionDep
):
    response =  await deposit_user(db_session, current_user, deposit)

    await create_log(db_session, "deposit_me", current_user)
    return response


@router.post(
    "/deposit",
    response_model=DepositResult
)
async def deposit(
        deposit_f_user: DepositForUser,
        current_user: CurrentUserDep,
        db_session: DBSessionDep
):
    response =  await deposit_for_user(db_session, deposit_f_user)

    await create_log(db_session, "deposit", current_user)
    return response


@router.post(
    "/withdraw/me",
    response_model=WithdrawResult
)
async def withdraw_me(
        withdraw: WithdrawUser,
        current_user: CurrentUserDep,
        db_session: DBSessionDep
):
    response = await withdraw_user(db_session, current_user, withdraw)

    await create_log(db_session, "withdraw_me", current_user)
    return response


@router.post(
    "/withdraw",
    response_model=WithdrawResult
)
async def withdraw_me(
        withdraw: WithdrawForUser,
        current_user: CurrentUserDep,
        db_session: DBSessionDep
):
    response = await withdraw_for_user(db_session, withdraw)

    await create_log(db_session, "withdraw", current_user)
    return response


@router.post(
    "/transfer/from_me",
    response_model=TransferResult
)
async def transfer_user(
        transfer: TransferUser,
        current_user: CurrentUserDep,
        db_session: DBSessionDep
):
    result = await transfer_users(db_session, current_user, transfer)

    await create_log(db_session, "transfer_from_me", current_user)
    return result


@router.post(
    "/transfer",
    response_model=TransferResult
)
async def transfer_userss(
        transfer: TransferForUser,
        current_user: CurrentUserDep,
        db_session: DBSessionDep
):
    result = await transfer_for_users(db_session, transfer)

    await create_log(db_session, "transfer", current_user)
    return result