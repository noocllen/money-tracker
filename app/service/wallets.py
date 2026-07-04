from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.schemas import CreateWalletRequest, WalletResponse
from app.repository import wallets as wallets_repository


def get_wallet(db: Session, current_user: User, wallet_name: str | None = None):
    # Если имя кошелька не указано - считаем общий баланс
    if wallet_name is None:
        # Суммируем все значения из словаря wallets
        wallets = wallets_repository.get_all_wallets(db, current_user.id)
        return {"total_balance": sum([w.balance for w in wallets])}
    # Проверяем существует ли запрашиваемый кошелек
    if not wallets_repository.is_wallet_exist(db, current_user.id, wallet_name):
        raise HTTPException(
            status_code=404,
            detail = f"Wallet '{wallet_name}' not found"
        )
    # Вовзращаем баланс конкретного кошелька
    wallet = wallets_repository.get_wallet_balance_by_name(db, current_user.id, wallet_name)
    return {"wallet": wallet.name, "balance": wallet.balance}

def create_wallet(db: Session, current_user: User, wallet: CreateWalletRequest) -> WalletResponse:
    # Проверяем не существует ли уже такой кошелек
    if wallets_repository.is_wallet_exist(db, current_user.id, wallet.name):
        raise HTTPException(
            status_code=400,
            detail=f"Wallet '{wallet.name}' already exists"
        )
    # Создаем новый кошелек с начальным балансом
    wallet = wallets_repository.create_wallet(db, current_user.id, wallet.name, wallet.initial_balance, wallet.currency)

    db.commit()
    # Возвращаем информацию о созданном кошельке
    return WalletResponse.model_validate(wallet)
