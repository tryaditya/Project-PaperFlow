import sys
from pathlib import Path

from PIL import Image, ImageOps

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QInputDialog,
)


SUPPORTED_IMAGE_FORMATS = {
    ".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"
}


class DropWidget(QWidget):
    """Central widget that accepts image files dragged into the app."""

    def __init__(self, paperflow):
        super().__init__()
        self.paperflow = paperflow
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        has_supported_image = any(
            url.isLocalFile()
            and Path(url.toLocalFile()).suffix.lower() in SUPPORTED_IMAGE_FORMATS
            for url in event.mimeData().urls()
        )

        if has_supported_image:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.isLocalFile()
            and Path(url.toLocalFile()).suffix.lower() in SUPPORTED_IMAGE_FORMATS
        ]

        if not files:
            QMessageBox.warning(
                self,
                "No supported images",
                "Please drop PNG, JPG, JPEG, BMP, WEBP or TIFF images.",
            )
            event.ignore()
            return

        event.acceptProposedAction()
        self.paperflow.convert_photos(files)


class PaperFlow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PAPERFLOW")
        self.resize(1000, 650)
        self.setMinimumSize(800, 550)

        self.setStyleSheet("""
            QMainWindow, QWidget#central {
                background-color: #F5F7FB;
                color: #202938;
                font-family: Segoe UI;
            }
            QLabel#brand {
                font-size: 28px;
                font-weight: 700;
                color: #3157D5;
            }
            QLabel#subtitle {
                font-size: 14px;
                color: #687386;
            }
            QFrame#toolCard {
                background-color: white;
                border: 1px solid #E1E6EF;
                border-radius: 14px;
            }
            QLabel#toolTitle {
                font-size: 21px;
                font-weight: 600;
            }
            QLabel#toolDescription {
                font-size: 13px;
                color: #687386;
            }
            QPushButton {
                background-color: #3157D5;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 18px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2445B5;
            }
        """)

        central = DropWidget(self)
        central.setObjectName("central")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(40, 35, 40, 35)
        main_layout.setSpacing(22)

        brand = QLabel("PAPERFLOW")
        brand.setObjectName("brand")

        subtitle = QLabel("Your documents, simplified.")
        subtitle.setObjectName("subtitle")

        main_layout.addWidget(brand)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(15)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        pdf_card = self.create_card(
            "Photos to PDF",
            "Combine multiple photos into one PDF, "
            "with each photo on its own page. You can also drag photos "
            "anywhere into this window.",
            "Select Photos",
            self.select_photos,
            drop_hint="↓  Drag & drop images here",
        )

        compress_card = self.create_card(
            "PDF Compressor",
            "Reduce the size of large PDF files "
            "while preserving the original file.",
            "Choose PDF",
            self.compress_pdf,
        )

        cards_layout.addWidget(pdf_card)
        cards_layout.addWidget(compress_card)
        main_layout.addLayout(cards_layout)
        main_layout.addStretch()

        footer = QLabel("PAPERFLOW  •  Simple. Private. Offline.")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #8791A2;")
        main_layout.addWidget(footer)

    def create_card(self, title, description, button_text, callback, drop_hint=None):
        card = QFrame()
        card.setObjectName("toolCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 28, 24, 28)
        layout.setSpacing(16)

        icon = QLabel("▣")
        icon.setStyleSheet(
            "font-size: 38px; color: #3157D5; border: none;"
        )

        heading = QLabel(title)
        heading.setObjectName("toolTitle")

        details = QLabel(description)
        details.setObjectName("toolDescription")
        details.setWordWrap(True)

        if drop_hint:
            hint = QLabel(drop_hint)
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint.setStyleSheet("""
                QLabel {
                    background-color: #EEF2FF;
                    color: #3157D5;
                    border: 2px dashed #9AAEF5;
                    border-radius: 10px;
                    padding: 16px 10px;
                    font-size: 14px;
                    font-weight: 600;
                }
            """)
            layout.addWidget(hint)

        button = QPushButton(button_text)
        button.clicked.connect(callback)

        layout.addWidget(icon)
        layout.addWidget(heading)
        layout.addWidget(details)
        layout.addStretch()
        layout.addWidget(button)

        return card

    def select_photos(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select photos",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff)",
        )

        if files:
            self.convert_photos(files)

    def convert_photos(self, files):
        if not files:
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF",
            "Photos.pdf",
            "PDF files (*.pdf)",
        )

        if not output_path:
            return

        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        images = []

        try:
            for file in files:
                with Image.open(file) as source:
                    image = ImageOps.exif_transpose(source)
                    image.load()

                    if image.mode == "RGBA":
                        background = Image.new("RGB", image.size, "white")
                        background.paste(
                            image, mask=image.getchannel("A")
                        )
                        image = background
                    else:
                        image = image.convert("RGB")

                    images.append(image.copy())

            if not images:
                QMessageBox.warning(
                    self,
                    "No images",
                    "No valid images were selected.",
                )
                return

            first_image, *remaining_images = images

            first_image.save(
                output_path,
                "PDF",
                save_all=True,
                append_images=remaining_images,
                resolution=150.0,
            )

            QMessageBox.information(
                self,
                "PDF created",
                f"Successfully created a PDF with {len(images)} page(s).\n\n"
                f"Saved to:\n{output_path}",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Conversion failed",
                f"Could not create the PDF:\n{error}",
            )

        finally:
            for image in images:
                image.close()

    def compress_pdf(self):
        input_path, _ = QFileDialog.getOpenFileName(
            self, "Choose a PDF to compress", "", "PDF files (*.pdf)"
        )

        if not input_path:
            return

        default_output = str(
            Path(input_path).with_name(
                Path(input_path).stem + "_compressed.pdf"
            )
        )

        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save compressed PDF", default_output, "PDF files (*.pdf)"
        )

        if not output_path:
            return

        if not output_path.lower().endswith(".pdf"):
            output_path += ".pdf"

        if Path(input_path).resolve() == Path(output_path).resolve():
            QMessageBox.warning(
                self,
                "Choose another file",
                "Please save the output to a different file.",
            )
            return

        quality = 30
        preset = "High — Maximum Compression"

        try:
            import pymupdf

            with pymupdf.open(input_path) as document:
                if document.needs_pass:
                    QMessageBox.warning(
                        self,
                        "Password-protected PDF",
                        "This PDF requires a password.",
                    )
                    return

                document.rewrite_images(
                    dpi_threshold=0,
                    dpi_target=0,
                    quality=quality,
                    lossy=True,
                    lossless=True,
                    color=True,
                    gray=True,
                    bitonal=True,
                )

                document.save(
                    output_path,
                    garbage=4,
                    deflate=True,
                    deflate_images=True,
                    deflate_fonts=True,
                )

            original = Path(input_path)
            output = Path(output_path)

            original_size = original.stat().st_size
            compressed_size = output.stat().st_size

            if compressed_size >= original_size:
                output.write_bytes(original.read_bytes())
                compressed_size = original_size
                result = (
                    "No reduction possible with this preset. "
                    "Original PDF preserved."
                )
            else:
                saved = original_size - compressed_size
                percentage = saved / original_size * 100

                result = (
                    f"Reduced by {saved / 1024:.1f} KB "
                    f"({percentage:.1f}%)."
                )

            QMessageBox.information(
                self,
                "Compression complete",
                f"Preset: {preset}\n"
                f"Original: {original_size / 1024:.1f} KB\n"
                f"Output: {compressed_size / 1024:.1f} KB\n\n"
                f"{result}\n\nSaved to:\n{output_path}",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Compression failed",
                f"Could not process this PDF:\n{error}",
            )


app = QApplication(sys.argv)
window = PaperFlow()
window.show()

sys.exit(app.exec())
