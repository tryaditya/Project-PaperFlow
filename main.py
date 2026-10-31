import sys
from pathlib import Path

from PIL import Image, ImageOps
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QInputDialog
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
)


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

        central = QWidget()
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
            "with each photo on its own page.",
            "Select Photos",
            self.select_photos,
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

    def create_card(self, title, description, button_text, callback):
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
            self,
            "Choose a PDF to compress",
            "",
            "PDF files (*.pdf)",
        )

        if not input_path:
            return

        default_output = str(
            Path(input_path).with_name(
                Path(input_path).stem + "_compressed.pdf"
            )
        )

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save compressed PDF",
            default_output,
            "PDF files (*.pdf)",
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

        presets = {
            "Low — Better Quality but Larger File Size": (85, 0),
            "Medium — Balanced": (60, 0),
            "High — Smaller File Size but Lower Quality": (30, 0),
        }

        preset, accepted = QInputDialog.getItem(
            self,
            "Compression level",
            "Choose a compression preset:",
            list(presets.keys()),
            1,
            False,
        )

        if not accepted:
            return

        quality, dpi_target = presets[preset]

        try:
            import pymupdf

            with pymupdf.open(input_path) as document:
                if document.needs_pass:
                    QMessageBox.warning(
                        self,
                        "Password-protected PDF",
                        "This PDF requires a password and cannot be "
                        "compressed by this version of PAPERFLOW.",
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

            original_size = Path(input_path).stat().st_size
            compressed_size = Path(output_path).stat().st_size
            saved = original_size - compressed_size

            percentage = (
                saved / original_size * 100
                if original_size > 0
                else 0
            )

            if saved > 0:
                result = (
                    f"Reduced by {saved / 1024:.1f} KB "
                    f"({percentage:.1f}%)."
                )
            elif saved < 0:
                result = (
                    f"The output is {abs(saved) / 1024:.1f} KB larger. "
                    "The original may already have been optimized."
                )
            else:
                result = "The file size did not change."

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
