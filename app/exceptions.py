class AppError(Exception):
    status_code = 500
    default_message = "Something went wrong. Please try again."

    def __init__(self, message=None, payload=None):
        self.message = message or self.default_message
        self.payload = payload or {}
        super().__init__(self.message)

    def to_dict(self):
        body = {"error": self.message}
        body.update(self.payload)
        return body


# ---------------------------------------------------------------------
# Upload / file validation errors -> app/routes/upload.py
# ---------------------------------------------------------------------

class FileError(AppError):
    """Base class for anything wrong with an uploaded file."""
    status_code = 400
    default_message = "There was a problem with the uploaded file."


class NoFileProvidedError(FileError):
    default_message = "No file was uploaded."


class UnsupportedFileTypeError(FileError):
    default_message = "That file type isn't supported. Please upload a PDF or DOCX."


class FileTooLargeError(FileError):
    status_code = 413
    default_message = "File is too large."


class CorruptedFileError(FileError):
    status_code = 422
    default_message = "The file appears to be corrupted or unreadable."


# ---------------------------------------------------------------------
# Parsing errors -> app/services/parser.py
# ---------------------------------------------------------------------

class ParsingError(AppError):
    """Raised when text/formatting extraction from a resume file fails."""
    status_code = 500
    default_message = "Failed to extract text from the file."


# ---------------------------------------------------------------------
# Request validation errors -> app/routes/analyze.py
# ---------------------------------------------------------------------

class MissingFieldError(AppError):
    status_code = 400
    default_message = "A required field is missing from the request."

    def __init__(self, field_name=None):
        self.field_name = field_name
        message = f"'{field_name}' is required." if field_name else self.default_message
        super().__init__(message)


class InvalidRequestError(AppError):
    status_code = 400
    default_message = "The request body is invalid or malformed."


# ---------------------------------------------------------------------
# Analysis / scoring errors -> analysis_pipeline.py, nlp.py, scorer.py
# ---------------------------------------------------------------------

class AnalysisError(AppError):
    status_code = 500
    default_message = "Failed to analyze the resume against the job description."


class TaxonomyLoadError(AnalysisError):
    default_message = "Failed to load the skill taxonomy."
