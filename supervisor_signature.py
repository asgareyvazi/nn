# === file: modules/supervisor_signature.py ===
from PySide2.QtWidgets import (
    QLineEdit, QPushButton, QCheckBox, QGroupBox,
    QVBoxLayout, QHBoxLayout, QLabel, QFormLayout,
    QMessageBox
)
from PySide2.QtGui import QPixmap, QPainter, QPen, QImage, QColor
from PySide2.QtCore import Qt, QPoint, QBuffer
from modules.base import ModuleBase


class SupervisorSignatureModule(ModuleBase):
    def __init__(self, parent=None):
        super().__init__("Supervisor Signature", parent)
        self.signature_image = None
        self.last_point = QPoint()
        self.drawing = False
        self._init_ui()
        self._bind_events()

    def _init_ui(self):
        # --- Signature Capture Area ---
        signature_group = QGroupBox("Signature Capture", self)
        signature_layout = QVBoxLayout(signature_group)

        self.signature_label = QLabel("Draw your signature here", self)
        self.signature_label.setFixedSize(450, 180)
        self.signature_label.setStyleSheet(
            "background-color: white; border: 1px solid #ccc;"
            "border-radius: 5px; font-style: italic; color: #888;"
        )
        self.signature_label.setAlignment(Qt.AlignCenter)

        # Signature action buttons
        btn_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Signature", self)
        self.save_btn = QPushButton("Save Signature", self)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch()

        signature_layout.addWidget(self.signature_label)
        signature_layout.addLayout(btn_layout)

        # --- Verification Section ---
        verification_group = QGroupBox("Verification", self)
        verification_layout = QFormLayout(verification_group)
        verification_layout.setContentsMargins(10, 15, 10, 15)

        self.supervisor_name = QLineEdit(self)
        self.supervisor_name.setPlaceholderText("Enter full name")
        
        self.operation_manager = QLineEdit(self)
        self.operation_manager.setPlaceholderText("Enter full name")
        
        self.verification_check = QCheckBox("I verify this report is accurate and complete", self)

        verification_layout.addRow("Supervisor Name:", self.supervisor_name)
        verification_layout.addRow("Operation Manager:", self.operation_manager)
        verification_layout.addRow(self.verification_check)

        # --- Preview Section ---
        preview_group = QGroupBox("Signature Preview", self)
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel(self)
        self.preview_label.setFixedSize(300, 120)
        self.preview_label.setStyleSheet(
            "background-color: white; border: 1px solid #ccc;"
            "border-radius: 5px;"
        )
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setText("Signature will appear here")
        
        preview_layout.addWidget(self.preview_label)

        # --- Layout Assembly ---
        self.scroll_layout.addWidget(signature_group)
        self.scroll_layout.addWidget(verification_group)
        self.scroll_layout.addWidget(preview_group)
        self.scroll_layout.addStretch()

    def _bind_events(self):
        self.signature_label.mousePressEvent = self._start_signature
        self.signature_label.mouseMoveEvent = self._draw_signature
        self.signature_label.mouseReleaseEvent = self._end_signature
        self.clear_btn.clicked.connect(self._clear_signature)
        self.save_btn.clicked.connect(self._save_signature)
        self.verification_check.stateChanged.connect(self._update_preview)

    def _start_signature(self, event):
        """Initialize drawing start point"""
        self.drawing = True
        if self.signature_image is None:
            # Create a blank signature canvas
            self.signature_image = QPixmap(self.signature_label.size())
            self.signature_image.fill(Qt.white)
            
            # Clear placeholder text
            self.signature_label.setText("")
            self.signature_label.setStyleSheet(
                "background-color: white; border: 1px solid #ccc; border-radius: 5px;"
            )
        
        self.last_point = event.position().toPoint()

    def _draw_signature(self, event):
        """Draw signature line segments"""
        if self.drawing and self.signature_image:
            painter = QPainter(self.signature_image)
            painter.setPen(QPen(Qt.black, 3, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(self.last_point, event.position().toPoint())
            painter.end()
            
            self.signature_label.setPixmap(self.signature_image)
            self.last_point = event.position().toPoint()
            
            # Update preview
            self._update_preview()

    def _end_signature(self, event):
        """End drawing session"""
        self.drawing = False

    def _clear_signature(self):
        """Clear the signature area"""
        self.signature_image = None
        self.signature_label.clear()
        self.signature_label.setText("Draw your signature here")
        self.signature_label.setStyleSheet(
            "background-color: white; border: 1px solid #ccc;"
            "border-radius: 5px; font-style: italic; color: #888;"
        )
        self.preview_label.setText("Signature will appear here")
        self.preview_label.setStyleSheet(
            "background-color: white; border: 1px solid #ccc;"
            "border-radius: 5px;"
        )

    def _update_preview(self):
        """Update signature preview"""
        if self.signature_image:
            # Scale signature for preview
            scaled = self.signature_image.scaled(
                self.preview_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)

    def _save_signature(self):
        """Save signature and verification info to database"""
        name = self.supervisor_name.text().strip()
        manager = self.operation_manager.text().strip()
        verified = self.verification_check.isChecked()

        # Validation
        errors = []
        if not name:
            errors.append("Supervisor name is required")
        if not manager:
            errors.append("Operation manager name is required")
        if not verified:
            errors.append("Verification checkbox must be checked")
        if not self.signature_image:
            errors.append("Signature is required")

        if errors:
            QMessageBox.warning(
                self, 
                "Validation Error", 
                "Please fix the following issues:\n• " + "\n• ".join(errors)
            )
            return

        # Convert QPixmap to bytes
        buffer = QBuffer()
        buffer.open(QBuffer.WriteOnly)
        self.signature_image.save(buffer, "PNG")
        image_bytes = buffer.data()

        # Save to database
        try:
            self.db.execute_query("DELETE FROM supervisor_signature", ())
            self.db.execute_query(
                "INSERT INTO supervisor_signature (supervisor_name, operation_manager, verified, signature_image) "
                "VALUES (?, ?, ?, ?)",
                (name, manager, int(verified), image_bytes)
            
            QMessageBox.information(
                self, 
                "Success", 
                "Signature and verification details saved successfully!"
            )
            self._clear_signature()
            self.supervisor_name.clear()
            self.operation_manager.clear()
            self.verification_check.setChecked(False)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Database Error", 
                f"Failed to save signature:\n{str(e)}"
            )