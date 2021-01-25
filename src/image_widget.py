from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPolygon

from .point import Point


class _DragMode:
    """Index of current bounding box being modified."""
    bbox_idx = None


class _SizeMode(_DragMode):
    """Index of which corner is being resized.

    0: top left
    1: top right
    2: bottom right
    3: bottom left
    """
    corner_idx = None

    def __init__(self, bbox_idx, corner_idx):
        self.bbox_idx = bbox_idx
        self.corner_idx = corner_idx


class _PositionMode(_DragMode):
    def __init__(self, bbox_idx):
        self.bbox_idx = bbox_idx


class ImageWidget(QtWidgets.QLabel):
    """Widget that displays the image along with bounding boxes."""
    # Radius of the drag handle
    DRAG_RADIUS = 6

    # We need to add a margin around the image since having a bbox around the entire image
    # caused drawing issues
    MARGIN = 5

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setFrameStyle(QtWidgets.QFrame.Box)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Upload Image")
        self.setMargin(ImageWidget.MARGIN)

        self.parent = parent

        # Current dragging mode if mouse is pressed (changing size or position)
        self.drag_mode = None

        # Previous location of mouse, used for finding delta position when changing position of bbox
        self.last_mouse_pos = None

    def img_to_qt(self, point):
        """Scale point from image dimension to qt dimension."""
        new_x = point.x / self.pixmap().rect().width() \
            * (self.rect().width() - 2 * ImageWidget.MARGIN) + ImageWidget.MARGIN
        new_y = point.y / self.pixmap().rect().height() \
            * (self.rect().height() - 2 * ImageWidget.MARGIN) + ImageWidget.MARGIN
        return Point(new_x, new_y)

    def qt_to_img(self, point):
        """Scale point from qt dimension to image dimension."""
        new_x = (point.x - ImageWidget.MARGIN) \
            / (self.rect().width() - 2 * ImageWidget.MARGIN) * self.pixmap().rect().width()
        new_y = (point.y - ImageWidget.MARGIN) \
            / (self.rect().height() - 2 * ImageWidget.MARGIN) * self.pixmap().rect().height()
        return Point(new_x, new_y)

    def bbox_to_polygon(self, bbox):
        """Unscaled bounding box to QPolygon"""
        scaled = [self.img_to_qt(point) for point in bbox]
        return QPolygon([QPoint(p.x, p.y) for p in scaled])

    def paintEvent(self, event):
        """Draws bounding box and dragging handle."""
        super().paintEvent(event)
        painter = QtGui.QPainter(self)

        for i, bbox in enumerate(self.parent.img_bboxes):
            if self.parent.color_change[i] == 0:
                painter.setPen(QtGui.QPen(Qt.blue, 3))
                # Draw bounding box
                painter.setBrush(Qt.NoBrush)  # No fill
                painter.drawPolygon(self.bbox_to_polygon(bbox))

                # Draw dragging handles
                painter.setBrush(QtGui.QBrush(Qt.blue))  # Fill blue

            elif self.parent.color_change[i] == 1:
                painter.setPen(QtGui.QPen(Qt.green, 3))
                painter.setBrush(QtGui.QBrush(Qt.green))

            elif self.parent.color_change[i] == 2:
                painter.setPen(QtGui.QPen(Qt.red, 3))
                painter.setBrush(QtGui.QBrush(Qt.red))

            # for showing all contents
            elif self.parent.color_change[i] == 6:
                painter.setPen(QtGui.QPen(Qt.darkBlue, 3))
                painter.setBrush(QtGui.QBrush(Qt.darkBlue))

            elif self.parent.color_change[i] == 7:
                painter.setPen(QtGui.QPen(Qt.darkYellow, 3))
                painter.setBrush(QtGui.QBrush(Qt.darkYellow))

            elif self.parent.color_change[i] == 8:
                painter.setPen(QtGui.QPen(Qt.darkMagenta, 3))
                painter.setBrush(QtGui.QBrush(Qt.darkMagenta))

            elif self.parent.color_change[i] == 9:
                painter.setPen(QtGui.QPen(Qt.darkCyan, 3))
                painter.setBrush(QtGui.QBrush(Qt.darkCyan))

            elif self.parent.color_change[i] == 10:
                painter.setPen(QtGui.QPen(Qt.darkGreen, 3))
                painter.setBrush(QtGui.QBrush(Qt.darkGreen))
            # ---

            # Draw bounding box
            painter.setBrush(Qt.NoBrush)  # No fill
            painter.drawPolygon(self.bbox_to_polygon(bbox))

            for point in bbox:
                scaled = self.img_to_qt(point)
                painter.drawEllipse(scaled.x - ImageWidget.DRAG_RADIUS,
                                    scaled.y - ImageWidget.DRAG_RADIUS,
                                    ImageWidget.DRAG_RADIUS * 2,
                                    ImageWidget.DRAG_RADIUS * 2)

            # Draw text ID
            scaled = self.img_to_qt(bbox[0])
            # painter.setPen(QtGui.QPen(Qt.white))
            # painter
            # painter.drawText(scaled.x + 10, scaled.y + 20, str(self.parent.img_names[i]))
            # painter.setPen(QtGui.QPen(Qt.black))

            painter_path = QtGui.QPainterPath()
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.strokePath(painter_path, QtGui.QPen(QtGui.QColor(0, 0, 0), 20, Qt.SolidLine))
            painter.fillPath(painter_path, QtGui.QColor(255, 255, 255))
            painter.drawText(scaled.x + 10, scaled.y + 20, str(self.parent.img_names[i]))

    def mousePressEvent(self, event):
        """Checks if the drag is changing size, position, or neither when mouse is pressed.

        Also updates the currently selected bbox in the main window.
        """
        super().mousePressEvent(event)
        for i, bbox in enumerate(self.parent.img_bboxes):
            selected = False
            for j, point in enumerate(bbox):
                # If cursor is in dragging circle
                scaled = self.img_to_qt(point)
                radius = (((event.pos().x() - scaled.x) ** 2 +
                           (event.pos().y() - scaled.y) ** 2))

                if radius < ImageWidget.DRAG_RADIUS ** 2:
                    self.drag_mode = _SizeMode(i, j)
                    selected = True

            # If cursor is within rectangle
            poly = self.bbox_to_polygon(bbox)
            mouse_pos = event.pos()
            if not selected and poly.containsPoint(mouse_pos, Qt.OddEvenFill):
                mg = 8
                small_poly = QPolygon([QPoint(poly[0].x() + mg, poly[0].y() + mg),
                                       QPoint(poly[1].x() - mg, poly[1].y() + mg),
                                       QPoint(poly[2].x() - mg, poly[2].y() - mg),
                                       QPoint(poly[3].x() + mg, poly[3].y() - mg)])
                if not small_poly.containsPoint(mouse_pos, Qt.OddEvenFill):
                    self.drag_mode = _PositionMode(i)
                    selected = True

            if selected:
                self.parent.color_change = len(self.parent.img_bboxes)*[False]
                self.parent.color_change[i] = True
                self.parent.img_bbox_idx = i
                self.parent.update_name_list_ui()
                self.parent.update_ui()
                break

    def mouseReleaseEvent(self, event):
        """Stops size/position change and update MainWindow when mouse is released."""
        super().mouseReleaseEvent(event)
        self.drag_mode = None
        self.last_mouse_pos = None

    def mouseMoveEvent(self, event):
        """Update bounding box to mouse while dragging."""
        super().mouseMoveEvent(event)
        if self.drag_mode and self.last_mouse_pos:
            bbox = self.parent.img_bboxes[self.drag_mode.bbox_idx]
            delta = Point(
                event.pos().x() - self.last_mouse_pos[0],
                event.pos().y() - self.last_mouse_pos[1]
            )

            corners = []

            if isinstance(self.drag_mode, _SizeMode):
                corners = [
                    (self.drag_mode.corner_idx, delta),
                    (
                        (self.drag_mode.corner_idx + 1) % 4,
                        Point(delta.x, 0) if self.drag_mode.corner_idx % 2 else Point(0, delta.y)

                    ),
                    (
                        (self.drag_mode.corner_idx - 1) % 4,
                        Point(0, delta.y) if self.drag_mode.corner_idx % 2 else Point(delta.x, 0)
                    )
                ]

            elif isinstance(self.drag_mode, _PositionMode):
                corners = [(i, delta) for i in range(len(bbox))]

            for corner in corners:
                bbox[corner[0]] = self.qt_to_img(self.img_to_qt(bbox[corner[0]]) + corner[1])

            self.update()

        self.last_mouse_pos = (event.pos().x(), event.pos().y())
