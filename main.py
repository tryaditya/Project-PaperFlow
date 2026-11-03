import sys
from pathlib import Path

from PIL import Image, ImageOps

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QBrush, QFont, QIcon, QPainter, QPen, QPixmap
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


class IllustrationWidget(QWidget):
    """Small vector illustrations for the two tool cards."""

    def __init__(self, kind, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.setMinimumHeight(145)
        self.setMaximumHeight(165)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        blue = QColor("#3157D5")
        light_blue = QColor("#E8EEFF")
        pale = QColor("#F4F6FF")
        dark = QColor("#20345F")
        red = QColor("#F04F59")

        cx = self.width() / 2
        cy = self.height() / 2

        if self.kind == "photos":
            # Two overlapping photo cards.
            painter.setPen(QPen(QColor("#C8D5FF"), 2))
            painter.setBrush(QBrush(light_blue))
            painter.save()
            painter.translate(cx - 40, cy - 4)
            painter.rotate(-10)
            painter.drawRoundedRect(-43, -48, 78, 96, 10, 10)
            painter.setBrush(QBrush(QColor("#9CC5FF")))
            painter.drawRoundedRect(-32, -35, 56, 43, 6, 6)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#5D91E8")))
            painter.drawEllipse(-16, -25, 13, 13)
            painter.drawPolygon([
                QPointF(-29, 5), QPointF(-9, -14), QPointF(2, -2),
                QPointF(13, -12), QPointF(25, 5)
            ])
            painter.restore()

            painter.setPen(QPen(blue, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QPointF(cx - 2, cy), QPointF(cx + 35, cy))
            painter.drawLine(QPointF(cx + 24, cy - 11), QPointF(cx + 36, cy))
            painter.drawLine(QPointF(cx + 24, cy + 11), QPointF(cx + 36, cy))

            # PDF page.
            painter.setPen(QPen(QColor("#C8D5FF"), 2))
            painter.setBrush(QBrush(Qt.GlobalColor.white))
            painter.drawRoundedRect(int(cx + 45), int(cy - 51), 65, 102, 9, 9)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(red))
            painter.drawRoundedRect(int(cx + 50), int(cy - 7), 55, 27, 6, 6)
            painter.setPen(QPen(Qt.GlobalColor.white))
            painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            painter.drawText(int(cx + 50), int(cy - 7), 55, 27, Qt.AlignmentFlag.AlignCenter, "PDF")

        else:
            # PDF document with compression arrows.
            painter.setPen(QPen(QColor("#C8D5FF"), 2))
            painter.setBrush(QBrush(light_blue))
            painter.drawRoundedRect(int(cx - 45), int(cy - 58), 90, 116, 12, 12)
            painter.setPen(QPen(QColor("#AFC2F8"), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QPointF(cx - 25, cy - 34), QPointF(cx + 20, cy - 34))
            painter.drawLine(QPointF(cx - 25, cy - 18), QPointF(cx + 10, cy - 18))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(red))
            painter.drawRoundedRect(int(cx - 34), int(cy - 2), 68, 29, 7, 7)
            painter.setPen(QPen(Qt.GlobalColor.white))
            painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            painter.drawText(int(cx - 34), int(cy - 2), 68, 29, Qt.AlignmentFlag.AlignCenter, "PDF")

            # Four inward arrows.
            painter.setPen(QPen(blue, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            for x1, y1, x2, y2, ax, ay in [
                (cx - 76, cy - 43, cx - 57, cy - 24, cx - 57, cy - 24),
                (cx + 76, cy - 43, cx + 57, cy - 24, cx + 57, cy - 24),
                (cx - 76, cy + 43, cx - 57, cy + 24, cx - 57, cy + 24),
                (cx + 76, cy + 43, cx + 57, cy + 24, cx + 57, cy + 24),
            ]:
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
                painter.drawLine(QPointF(x2, y2), QPointF(x2 + (7 if x1 < x2 else -7), y2))
                painter.drawLine(QPointF(x2, y2), QPointF(x2, y2 + (7 if y1 < y2 else -7)))

        painter.end()


class PaperFlow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PAPERFLOW")
        self.setWindowIcon(QIcon(str(Path(__file__).with_name("paperflow.ico"))))
        self.resize(1050, 700)
        self.setMinimumSize(850, 620)

        self.setStyleSheet("""
            QMainWindow, QWidget#central {
                background-color: #F3F6FF;
                color: #18233B;
                font-family: Segoe UI;
            }
            QLabel#brand {
                font-size: 34px;
                font-weight: 800;
                color: #244BCB;
            }
            QLabel#subtitle {
                font-size: 15px;
                color: #657394;
            }
            QLabel#eyebrow {
                color: #3157D5;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            QFrame#toolCard {
                background-color: #FFFFFF;
                border: 1px solid #DDE5FA;
                border-radius: 20px;
            }
            QLabel#toolTitle {
                font-size: 22px;
                font-weight: 700;
                color: #18233B;
            }
            QLabel#toolDescription {
                font-size: 13px;
                color: #657394;
            }
            QLabel#dropHint {
                background-color: #F0F4FF;
                color: #3157D5;
                border: 2px dashed #9AAEF5;
                border-radius: 12px;
                padding: 13px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton {
                background-color: #3157D5;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 13px 18px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #2445B5; }
            QPushButton:pressed { background-color: #1D3998; }
            QPushButton:focus { border: 2px solid #91A9FF; }
        """)

        central = DropWidget(self)
        central.setObjectName("central")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(42, 32, 42, 28)
        main_layout.setSpacing(10)

        brand_row = QHBoxLayout()
        brand_icon = QLabel()
        brand_icon.setPixmap(QPixmap(str(Path(__file__).with_name("paperflow_icon.png"))).scaled(
            66, 66, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        brand_row.addWidget(brand_icon)

        brand_text = QVBoxLayout()
        brand = QLabel("PAPERFLOW")
        brand.setObjectName("brand")
        subtitle = QLabel("Your documents, simplified.")
        subtitle.setObjectName("subtitle")
        brand_text.addWidget(brand)
        brand_text.addWidget(subtitle)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()
        main_layout.addLayout(brand_row)
        main_layout.addSpacing(18)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(22)

        pdf_card = self.create_card(
            "Photos to PDF",
            "Turn your photos into a clean, shareable PDF. Each image gets its own page.",
            "Select Photos",
            self.select_photos,
            "photos",
            "↓   Drag & drop images here",
        )
        compress_card = self.create_card(
            "PDF Compressor",
            "Make large PDF files smaller while keeping your original file safe.",
            "Choose PDF",
            self.compress_pdf,
            "compress",
        )

        cards_layout.addWidget(pdf_card, 1)
        cards_layout.addWidget(compress_card, 1)
        main_layout.addLayout(cards_layout, 1)
        main_layout.addStretch()

        footer = QLabel("PAPERFLOW   •   Simple. Private. Offline.")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #8794B2; font-size: 12px; padding-top: 8px;")
        main_layout.addWidget(footer)

    def create_card(self, title, description, button_text, callback, illustration, drop_hint=None):
        card = QFrame()
        card.setObjectName("toolCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 24, 25, 24)
        layout.setSpacing(12)

        eyebrow = QLabel("IMAGE TO DOCUMENT" if illustration == "photos" else "OPTIMIZE YOUR FILE")
        eyebrow.setObjectName("eyebrow")

        if drop_hint:
            hint = QLabel(drop_hint)
            hint.setObjectName("dropHint")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(hint)

        graphic = IllustrationWidget(illustration)
        heading = QLabel(title)
        heading.setObjectName("toolTitle")

        details = QLabel(description)
        details.setObjectName("toolDescription")
        details.setWordWrap(True)

        button = QPushButton(button_text)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(callback)

        layout.addWidget(eyebrow)
        layout.addWidget(graphic)
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
