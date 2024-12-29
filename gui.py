import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QMenuBar, QMenu, QAction, QMessageBox
)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QPen


class CoordinateSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coordinate System")
        self.setGeometry(100, 100, 600, 600)

        # Set up the graphics view and scene
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setGeometry(0, 0, 600, 600)
        self.setCentralWidget(self.view)

        # Flask server URL
        self.server_url = "http://127.0.0.1:5000"

        # Draw the coordinate grid
        self.draw_grid()

        # Load existing points from the backend
        self.load_points()

        # Set up menu
        self.create_menu()

    def create_menu(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        home_menu = menu_bar.addMenu("Home")
        plotted_points_menu = menu_bar.addMenu("Plotted Points")

        home_action = QAction("Home", self)
        home_action.triggered.connect(self.display_home)
        home_menu.addAction(home_action)

        plotted_points_action = QAction("Plotted Points", self)
        plotted_points_action.triggered.connect(self.display_plotted_points)
        plotted_points_menu.addAction(plotted_points_action)

    def display_home(self):
        self.scene.clear()
        self.draw_grid()
        self.load_points()

    def display_plotted_points(self):
        try:
            response = requests.get(f"{self.server_url}/get_points")
            if response.status_code == 200:
                points = response.json()
                if points:
                    points_str = "\n".join([f"({x}, {y})" for x, y in points])
                    QMessageBox.information(self, "Plotted Points", f"Plotted Points:\n{points_str}")
                else:
                    QMessageBox.information(self, "Plotted Points", "No points have been plotted yet.")
            else:
                QMessageBox.warning(self, "Error", f"Failed to load points: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error connecting to backend: {e}")

    def draw_grid(self):
        # Draw axes
        pen = QPen(Qt.black)
        pen.setWidth(2)
        self.scene.addLine(0, 300, 600, 300, pen)  # X-axis
        self.scene.addLine(300, 0, 300, 600, pen)  # Y-axis

        # Draw grid lines
        pen.setWidth(1)
        pen.setColor(Qt.gray)
        for i in range(0, 601, 20):
            self.scene.addLine(i, 0, i, 600, pen)  # Vertical lines
            self.scene.addLine(0, i, 600, i, pen)  # Horizontal lines

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Map the mouse click to scene coordinates
            scene_pos = self.view.mapToScene(event.pos())
            x, y = scene_pos.x(), scene_pos.y()

            # Translate to Cartesian coordinates
            x -= 300
            y = 300 - y

            # Save the point to the backend
            self.save_point_to_backend(x, y)

            # Draw the point
            self.draw_point(scene_pos)

    def save_point_to_backend(self, x, y):
        try:
            response = requests.post(f"{self.server_url}/save_point", json={"x": x, "y": y})
            if response.status_code == 200:
                print(f"Point saved: {x, y}")
            else:
                print(f"Error saving point: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to backend: {e}")

    def load_points(self):
        try:
            response = requests.get(f"{self.server_url}/get_points")
            if response.status_code == 200:
                points = response.json()
                for point in points:
                    self.draw_point(QPointF(point[0] + 300, 300 - point[1]))
                print(f"Loaded points: {points}")
            else:
                print(f"Error loading points: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to backend: {e}")

    def draw_point(self, point):
        # Draw a small circle at the clicked point
        radius = 3
        self.scene.addEllipse(point.x() - radius, point.y() - radius, radius * 2, radius * 2, QPen(Qt.red), Qt.red)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoordinateSystem()
    window.show()
    sys.exit(app.exec_())