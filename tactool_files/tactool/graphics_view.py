"""
The Graphics View is the user interface element in charge of image interaction.
It can load and save images and is responsible for capturing mouse events.
"""

import math

from PyQt5.QtCore import (
    pyqtSignal,
    QPointF,
    QRectF,
    Qt,
)
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPixmap,
    QWheelEvent,
)
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsPixmapItem,
    QGraphicsView,
)

from tactool.graphics_scene import GraphicsScene


class GraphicsView(QGraphicsView):
    """
    PyQt QGraphicsView with convenience functions for modifications.
    Also includes functions for user interaction with the Graphics View.
    """
    # These track if the user does a left or right click
    # Both returning coordinates of the button click
    left_click = pyqtSignal(int, int)
    right_click = pyqtSignal(int, int)
    # Tracking for recoordination
    recoordinate_up = pyqtSignal()
    recoordinate_down = pyqtSignal()
    recoordinate_left = pyqtSignal()
    recoordinate_right = pyqtSignal()

    # Tracks the users mouse movement on the Graphics View whilst in scaling mode
    scale_move_event = pyqtSignal(float)


    def __init__(self) -> None:
        super().__init__()
        self._zoom = 0
        # This stores a boolean to determine if there is currently an image loaded in the PyQt Graphics View
        self._empty = True
        # This stores the current image of the PyQt Graphics View as a PyQt Pixmap Item
        self._image = QGraphicsPixmapItem()
        self.navigation_mode = False
        # Setting scaling variables
        self.set_scale_mode = False
        self.scale_start_point = QPointF()
        self.scale_end_point = QPointF()

        # Create the Graphics Scene which is displayed in the Graphics View
        self.graphics_scene = GraphicsScene()
        # This adds the current image to the Graphics Scene
        self.graphics_scene.addItem(self._image)
        self.setScene(self.graphics_scene)
        self.configure_frame()


    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Function to handle mouse clicking interaction events with the Graphics View.

        Since we are only adding functionality to mousePressEvent, we pass the event to the
        parent PyQt class, QGraphicsView, at the end of the function to handle
        all other event occurences.
        """
        # If the user clicks anywhere on the current image
        if self._image.isUnderMouse():
            clicked_point = self.mapToScene(event.pos()).toPoint()

            if self.set_scale_mode:
                # If there is no current start point of a scaling line
                if self.scale_start_point.isNull():
                    # Set the start point of the scaling line to be the clicked point
                    self.scale_start_point = clicked_point
                    # Call the Graphics Scene function to draw the point
                    self.graphics_scene.draw_scale_point(clicked_point.x(), clicked_point.y())

                # Else if there is a current start point but not an end point of a scaling line
                elif not self.scale_start_point.isNull() and self.scale_end_point.isNull():
                    # Set the end point of the scaling line to be the clicked point
                    self.scale_end_point = clicked_point
                    # Call the Graphics Scene function to draw the point
                    self.graphics_scene.draw_scale_point(clicked_point.x(), clicked_point.y())

            elif not self.navigation_mode:
                clicked_button = event.button()

                if clicked_button == Qt.LeftButton:
                    self.left_click.emit(clicked_point.x(), clicked_point.y())

                elif clicked_button == Qt.RightButton:
                    self.right_click.emit(clicked_point.x(), clicked_point.y())
        super().mousePressEvent(event)


    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Function to handle mouse movement interaction events with the Graphics View.

        Since we are only adding functionality to mouseMoveEvent, we pass the event to the
        parent PyQt class, QGraphicsView, at the end of the function to handle
        all other event occurences.
        """
        if self.set_scale_mode:
            # If there is a current start point but not an end point of a scaling line
            if not self.scale_start_point.isNull() and self.scale_end_point.isNull():
                # Emit a signal that the mouse has been moved
                # Passing the start point of the scaling line and the coordinates of the mouse
                start, end = self.scale_start_point, self.mapToScene(event.pos()).toPoint()
                pixel_distance = round(math.sqrt((start.y() - end.y())**2 + (start.x() - end.x())**2), 2)
                self.graphics_scene.draw_scale_line(start, end)
                self.scale_move_event.emit(pixel_distance)
        super().mouseMoveEvent(event)


    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Function to handle mouse scroll wheel interaction events with the Graphics View.

        The function does not pass the event back to the parent class PyQt QGraphicsView
        because the default wheelEvent triggers the scrolling of the Graphics View.
        But we want to make wheelEvent trigger custom zooming instead.
        """
        # If there is currently an image in the Graphics View
        # and the program is currently in navigation mode
        if not self._empty and self.navigation_mode:

            # If the mouse wheel scrolled up
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            # Else if the mouse wheel scrolled down
            elif event.angleDelta().y() < 0:
                factor = 0.8
                self._zoom -= 1

            # If the current image is zoomed in
            if self._zoom > 0:
                # Scale the zoom to the new values
                self.scale(factor, factor)

            # Else if the image is currently meant to be fully zoomed out
            elif self._zoom == 0:
                self.show_entire_image()

            # Else if the zoom value is below 0, reset it
            elif self._zoom < 0:
                self._zoom = 0


    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Function to handle keyboard press events.

        Since we are only adding functionality to keyPressEvent, we pass the event to the
        parent PyQt class, QGraphicsView, at the end of the function to handle
        all other event occurences.
        """
        if self.set_scale_mode is False:
            key = event.key()
            recoordination_directions = {
                Qt.Key.Key_W: self.recoordinate_up,
                Qt.Key.Key_S: self.recoordinate_down,
                Qt.Key.Key_A: self.recoordinate_left,
                Qt.Key.Key_D: self.recoordinate_right,
            }
            if key in recoordination_directions and self.navigation_mode:
                recoordination_directions[event.key()].emit()

            # isAutoRepeat prevents the function from spamming whilst holding the key down
            elif not event.isAutoRepeat():
                # If the 'Ctrl' key is pressed
                if event.key() == Qt.Key_Control:
                    # Enable navigation mode
                    self.navigation_mode = True
                    self.setDragMode(QGraphicsView.ScrollHandDrag)

        super().keyPressEvent(event)


    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        """
        Function to handle keyboard release events.

        Since we are only adding functionality to keyReleaseEvent, we pass the event to the
        parent PyQt class, QGraphicsView, at the end of the function to handle
        all other event occurences.
        """
        # If the 'Ctrl' key is released
        if event.key() == Qt.Key_Control:
            # Disable navigation mode
            self.navigation_mode = False
            self.setDragMode(QGraphicsView.NoDrag)
        super().keyReleaseEvent(event)


    def configure_frame(self) -> None:
        """
        Function to configure the settings of the Graphics View.
        """
        # Sets the Graphics View to anchor it's centre to the current position of the mouse
        # This applies when zooming into the image
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        # Disabling the PyQt Graphics View scroll bars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Setting the background colour of the PyQt Graphics View
        # Represents RGB and a 4th value sets how opaque the colour is, 0 being transparent
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameStyle(QFrame.NoFrame)


    def load_image(self, filepath: str) -> None:
        """
        Fuction to load an image from a given path into the Graphics View as a PyQt Pixmap.
        """
        # Load the image into a PyQt Pixmap
        pixmap = QPixmap(filepath)
        # Reset the zoom value
        self._zoom = 0
        # If a pixmap currently exists and it is not empty
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._image.setPixmap(pixmap)

        # Else the image is bad
        else:
            # Set the image of the Graphics View to be an empty Pixmap
            self._empty = True
            self._image.setPixmap(QPixmap())
        self.show_entire_image()


    def save_image(self, filepath: str) -> None:
        """
        Function to get the current Graphics Scene state and save it to a given file.
        """
        # If you get the size of the Graphics Scene rather than the Graphics View,
        # then the saved image includes points which go over the border of the imported image
        rect = self.sceneRect().toRect()
        # Create a new pixmap the same as the rect
        pixmap = QPixmap(rect.size())
        # Create a rectF of the pixmap size
        rectf = QRectF(pixmap.rect())
        # Define the painter for rendering
        painter = QPainter(pixmap)
        # Render the Graphics Scene onto the pixmap
        self.graphics_scene.render(painter, rectf, rectf)
        # Save the pixmap to the given file
        pixmap.save(filepath)
        # You need to explicitly tell the painter object we are done here
        painter.end()


    def show_entire_image(self) -> None:
        """
        Function to show the entirety of the current image in the Graphics View.
        """
        # Get a rectf of the current image
        rect = QRectF(self._image.pixmap().rect())
        # If a rectf object was successfully created
        if not rect.isNull():

            # Set the rect of the Graphics Scene to be the rect of the current image
            self.setSceneRect(rect)
            # If there is currently an image in the Graphics View
            if not self._empty:

                # Create a rect of the current view in the Graphics View
                viewrect = self.viewport().rect()
                # Create a rect of the entire Graphics Scene
                scenerect = self.transform().mapRect(rect)
                # Calculate the zoom changes required to fit the entire Graphics Scene into the Graphics View
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                # Set the new zoom scale of the Graphics View
                self.scale(factor, factor)

            # Reset the zoom value
            self._zoom = 0


    def toggle_scaling_mode(self) -> None:
        """
        Function to toggle the scaling mode Graphics Scene settings.
        """
        self.set_scale_mode = not self.set_scale_mode
        self.graphics_scene.toggle_transparent_window(self._image)

        # If the program is currently in Scaling mode
        if self.set_scale_mode:
            # Set the Graphics View cursor to a crosshair
            self.setCursor(Qt.CrossCursor)
        # Else when the program is not currently in Scaling mode
        else:
            # Reset the scaling mode attributes to normal
            self.graphics_scene.remove_scale_items()
            self.reset_scale_line_points()
            self.setCursor(Qt.ArrowCursor)


    def reset_scale_line_points(self) -> None:
        """
        Function to reset the scaling line points to be blank QPointF objects.
        """
        self.scale_start_point = QPointF()
        self.scale_end_point = QPointF()
