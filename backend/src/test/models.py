from settings.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column

class Product(Base):
    __tablename__ = 'products'

    name: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()
