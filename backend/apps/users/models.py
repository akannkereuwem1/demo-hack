import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.TextChoices):
    """Defines the two user roles in the AgroNet platform."""
    FARMER = 'farmer', 'Farmer'
    BUYER = 'buyer', 'Buyer'


class UserManager(BaseUserManager):
    """Custom manager for the User model that uses email as the unique identifier."""

    def create_user(self, email: str, password: str, role: str, **extra_fields) -> 'User':
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set.')
        if not role:
            raise ValueError('The Role field must be set.')

        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)  # Uses bcrypt via PASSWORD_HASHERS in settings
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields) -> 'User':
        """Create and return a superuser with all permissions."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', Role.FARMER)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for AgroNet.

    Uses email as the primary authentication identifier.
    Supports two roles: farmer and buyer.
    Uses UUID as primary key.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.BUYER,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.email} ({self.role})'

    @property
    def is_farmer(self) -> bool:
        """Returns True if the user has the farmer role."""
        return self.role == Role.FARMER

    @property
    def is_buyer(self) -> bool:
        """Returns True if the user has the buyer role."""
        return self.role == Role.BUYER
