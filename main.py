"""PySide6 interface for a rocket-propulsion trajectory assignment.

The calculation functions in this module are intentional placeholders. Replace
their TODO sections with the assignment's physics and numerical methods.
"""

import math
import os
import sys

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def calculate_atmosphere(h):
    """חישוב טמפרטורה, לחץ וצפיפות אוויר כפונקציה של הגובה h במטרים."""
    g0 = 9.81
    R = 287.0

    if h < 11000:
        T = 288.0 - 0.0064864 * h
        P_atm = (1.0 - 2.256944e-5 * h) ** 5.2586
    else:
        h_km = h / 1000.0
        if h < 20000:
            T = 216.65
        elif h < 33000:
            T = 216.65 + 0.99 * (h_km - 20.0)
        else:
            T = 139.7 + 2.7661 * h_km

        P_atm = math.exp((-g0 * (h - 1000.0)) / (R * T))

    # המרת לחץ מאטמוספירות לפסקל וחישוב צפיפות
    P_pa = P_atm * 101325.0
    rho = P_pa / (R * T)
    return T, P_atm, rho


def calculate_single_step(
    h0=2000.0,
    Isp=260.0,
    theta=50.0,
    m_dot=15.0,
    CD=0.2,
    m0=200.0,
    Af=0.1,
    M=1.0,
    tb=7.0,
    dt=0.5,
):
    """סעיף א': חישוב מצב הטיל לאחר צעד יחיד של 0.5 שניות לפי נתוני ההתחלה."""
    g0 = 9.81
    R = 287.0
    gamma = 1.4

    # תנאי התחלה
    T0, P0, rho0 = calculate_atmosphere(h0)
    a0 = math.sqrt(gamma * R * T0)
    v0 = M * a0

    theta_rad = math.radians(theta)
    vx0 = v0 * math.cos(theta_rad)
    vy0 = v0 * math.sin(theta_rad)

    # כוחות ברגע ההתחלה
    thrust = Isp * m_dot * g0
    drag = 0.5 * rho0 * (v0**2) * CD * Af

    # תאוצות
    ax = ((thrust - drag) * math.cos(theta_rad)) / m0
    ay = ((thrust - drag) * math.sin(theta_rad)) / m0 - g0

    # עדכון לאחר צעד יחיד dt = 0.5 s
    vx = vx0 + ax * dt
    vy = vy0 + ay * dt
    v = math.sqrt(vx**2 + vy**2)
    x = vx0 * dt
    h = h0 + vy0 * dt
    m = m0 - m_dot * dt

    return {
        "t": dt,
        "h": h,
        "x": x,
        "v": v,
        "vx": vx,
        "vy": vy,
        "m": m,
    }


def simulate_trajectory(
    h0=2000.0,
    Isp=260.0,
    theta=50.0,
    m_dot=15.0,
    CD=0.2,
    m0=200.0,
    Af=0.1,
    M=1.0,
    tb=7.0,
    dt=0.01,
):
    """סעיף ב': חישוב מסלול הטיל באמצעות לולאת while עד הפגיעה בקרקע."""
    g0 = 9.81
    R = 287.0
    gamma = 1.4

    # תנאי התחלה ברגע t = 0
    T0, P0, rho0 = calculate_atmosphere(h0)
    a0 = math.sqrt(gamma * R * T0)
    v0 = M * a0

    theta_rad = math.radians(theta)
    vx = v0 * math.cos(theta_rad)
    vy = v0 * math.sin(theta_rad)

    t = 0.0
    h = h0
    x = 0.0
    m = m0

    # רשימות לשמירת הנתונים לאורך המסלול
    times = [t]
    altitudes = [h]
    distances = [x]
    velocities = [v0]
    masses = [m]

    # לולאת while הרצה כל עוד הטיל באוויר (h > 0)
    while h > 0 and t < 1000.0:
        v = math.sqrt(vx**2 + vy**2)
        T, P_atm, rho = calculate_atmosphere(h)

        # בדיקה האם המנוע עדיין בוער או שכבר כבה
        if round(t, 6) < tb:
            thrust = Isp * m_dot * g0
            dm = m_dot * dt
        else:
            thrust = 0.0
            dm = 0.0

        drag = 0.5 * rho * (v**2) * CD * Af

        # כיוון הדחף והגרר הוא לאורך וקטור המהירות (cos = vx/v, sin = vy/v)
        ax = ((thrust - drag) * (vx / v)) / m
        ay = ((thrust - drag) * (vy / v)) / m - g0

        # נתוני סיום הצעד יהוו את נתוני ההתחלה לצעד הבא
        x = x + vx * dt
        h = h + vy * dt
        vx = vx + ax * dt
        vy = vy + ay * dt
        m = m - dm
        t = t + dt

        v_new = math.sqrt(vx**2 + vy**2)

        times.append(t)
        altitudes.append(h)
        distances.append(x)
        velocities.append(v_new)
        masses.append(m)

    return {
        "t": np.array(times),
        "h": np.array(altitudes),
        "x": np.array(distances),
        "v": np.array(velocities),
        "m": np.array(masses),
    }


class AboutDialog(QDialog):
    """חלון מידע על הפרויקט עם קישור ל-GitHub."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Rocket Trajectory")
        self.setModal(True)
        self.setMinimumWidth(390)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(12)

        heading = QLabel("Rocket Propulsion")
        heading.setObjectName("aboutHeading")
        layout.addWidget(heading)

        description = QLabel(
            "Trajectory simulation assignment interface\n"
            "Interactive plots for altitude, distance, trajectory, velocity, "
            "and rocket mass."
        )
        description.setObjectName("aboutDescription")
        description.setWordWrap(True)
        layout.addWidget(description)

        repository = QLabel(
            '<a href="https://github.com/idone2014-hub/Rcket_Bonus_2">'
            "View project repository</a>"
        )
        repository.setOpenExternalLinks(True)
        repository.setTextInteractionFlags(Qt.TextBrowserInteraction)
        layout.addWidget(repository)

        close_button = QPushButton("Close")
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignRight)


class RocketTrajectoryWindow(QMainWindow):
    """החלון הראשי המציג את תפריט הגרפים ואת הגרף האינטראקטיבי."""

    GRAPHS = {
        "altitude": {
            "button": "Altitude vs. Time",
            "title": "Altitude vs. Time",
            "xlabel": "Time, t [s]",
            "ylabel": "Altitude, h [m]",
        },
        "distance": {
            "button": "Horizontal Distance vs. Time",
            "title": "Horizontal Distance vs. Time",
            "xlabel": "Time, t [s]",
            "ylabel": "Horizontal distance, x [m]",
        },
        "trajectory": {
            "button": "Rocket Trajectory",
            "title": "Rocket Trajectory (h vs. x)",
            "xlabel": "Horizontal distance, x [m]",
            "ylabel": "Altitude, h [m]",
        },
        "velocity": {
            "button": "Velocity vs. Time",
            "title": "Velocity vs. Time",
            "xlabel": "Time, t [s]",
            "ylabel": "Velocity, v [m/s]",
        },
        "mass": {
            "button": "Rocket Mass vs. Time",
            "title": "Rocket Mass vs. Time",
            "xlabel": "Time, t [s]",
            "ylabel": "Rocket mass, m [kg]",
        },
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rocket Propulsion | Trajectory Simulator")
        self.resize(1180, 760)
        self.setMinimumSize(900, 600)

        # הרצת החישובים של סעיף א' וסעיף ב' בעת עליית התוכנית
        self.part_a = calculate_single_step()
        self.results = simulate_trajectory()

        print(f"Part A (t = 0.5 s): Velocity = {self.part_a['v']:.2f} m/s")

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 26, 20, 22)
        sidebar_layout.setSpacing(10)

        brand = QLabel("ORBITAL")
        brand.setObjectName("brandLabel")
        sidebar_layout.addWidget(brand)

        subtitle = QLabel("ROCKET TRAJECTORY")
        subtitle.setObjectName("sidebarSubtitle")
        sidebar_layout.addWidget(subtitle)

        nav_heading = QLabel("VISUALIZATIONS")
        nav_heading.setObjectName("sectionLabel")
        sidebar_layout.addWidget(nav_heading)
        sidebar_layout.addSpacing(4)

        self.navigation_buttons = {}
        for graph_type, graph in self.GRAPHS.items():
            button = QPushButton(graph["button"])
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setMinimumHeight(44)
            button.clicked.connect(
                lambda checked, selected=graph_type: self.plot_graph(selected)
            )
            sidebar_layout.addWidget(button)
            self.navigation_buttons[graph_type] = button

        sidebar_layout.addStretch(1)
        about_button = QPushButton("About this project")
        about_button.setObjectName("aboutButton")
        about_button.setMinimumHeight(42)
        about_button.clicked.connect(self.show_about_dialog)
        sidebar_layout.addWidget(about_button)
        root_layout.addWidget(sidebar)

        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 26, 30, 28)
        content_layout.setSpacing(18)

        page_title = QLabel("Flight analysis")
        page_title.setObjectName("pageTitle")
        content_layout.addWidget(page_title)

        page_description = QLabel(
            f"Part A (t = 0.5 s): v = {self.part_a['v']:.2f} m/s  |  "
            f"Part B: Max altitude = {np.max(self.results['h']):.1f} m"
        )
        page_description.setObjectName("pageDescription")
        content_layout.addWidget(page_description)

        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(12, 12, 12, 12)
        chart_layout.setSpacing(6)

        self.figure = Figure(figsize=(8, 5), dpi=100, facecolor="#ffffff")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, chart_frame)
        chart_layout.addWidget(self.toolbar)
        chart_layout.addWidget(self.canvas, 1)
        content_layout.addWidget(chart_frame, 1)
        root_layout.addWidget(content, 1)

        self.plot_graph("altitude")

    def plot_graph(self, graph_type):
        """ציור הגרף הנבחר מתוך תוצאות הסימולציה."""
        graph = self.GRAPHS[graph_type]

        t = self.results["t"]
        h = self.results["h"]
        x = self.results["x"]
        v = self.results["v"]
        m = self.results["m"]

        if graph_type == "altitude":
            x_values, y_values = t, h
        elif graph_type == "distance":
            x_values, y_values = t, x
        elif graph_type == "trajectory":
            x_values, y_values = x, h
        elif graph_type == "velocity":
            x_values, y_values = t, v
        else:
            x_values, y_values = t, m

        self.figure.clear()
        axes = self.figure.add_subplot(111)
        axes.plot(x_values, y_values, color="#3977e8", linewidth=2.5)
        axes.set_title(graph["title"], pad=16, fontweight="bold")
        axes.set_xlabel(graph["xlabel"])
        axes.set_ylabel(graph["ylabel"])
        axes.grid(True, color="#e7ebf2", linewidth=0.8)
        axes.set_xlim(left=0)
        axes.set_ylim(bottom=0)
        axes.margins(x=0.04, y=0.08)
        self.figure.tight_layout()
        self.canvas.draw_idle()

        for key, button in self.navigation_buttons.items():
            button.setChecked(key == graph_type)

    def show_about_dialog(self):
        """פתיחת חלון האודות."""
        AboutDialog(self).exec()


def main():
    """הפעלת האפליקציה וטעינת קובץ העיצוב style.qss."""
    app = QApplication(sys.argv)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    stylesheet_path = os.path.join(base_dir, "style.qss")

    if os.path.isfile(stylesheet_path):
        with open(stylesheet_path, "r", encoding="utf-8") as file:
            app.setStyleSheet(file.read())

    window = RocketTrajectoryWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()