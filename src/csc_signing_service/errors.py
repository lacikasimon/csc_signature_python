class SigningServiceError(RuntimeError):
    """Base class for service-layer failures."""


class InvalidPDFError(SigningServiceError):
    """Raised when input bytes are not a usable PDF."""


class CSCProviderError(SigningServiceError):
    """Raised when the CSC provider rejects or fails a request."""


class CSCProviderTimeoutError(CSCProviderError):
    """Raised when the CSC provider does not respond in time."""
