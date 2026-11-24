from pathlib import Path

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def calculate_atmosphere(h):
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

        P_atm = np.exp((-g0 * (h - 1000.0)) / (R * T))

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
    g0 = 9.81
    R = 287.0
    gamma = 1.4

    T0, P0, rho0 = calculate_atmosphere(h0)
    a0 = np.sqrt(gamma * R * T0)
    v0 = M * a0

    theta_rad = theta * np.pi / 180.0
    vx0 = v0 * np.cos(theta_rad)
    vy0 = v0 * np.sin(theta_rad)

    thrust = Isp * m_dot * g0
    drag = 0.5 * rho0 * (v0**2) * CD * Af

    ax = ((thrust - drag) * np.cos(theta_rad)) / m0
    ay = ((thrust - drag) * np.sin(theta_rad)) / m0 - g0

    vx = vx0 + ax * dt
    vy = vy0 + ay * dt
    v = np.sqrt(vx**2 + vy**2)
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
    g0 = 9.81
    R = 287.0
    gamma = 1.4

    T0, P0, rho0 = calculate_atmosphere(h0)
    a0 = np.sqrt(gamma * R * T0)
    v0 = M * a0

    theta_rad = theta * np.pi / 180.0
    vx = v0 * np.cos(theta_rad)
    vy = v0 * np.sin(theta_rad)

    t = 0.0
    h = h0
    x = 0.0
    m = m0
    max_h = h0

    times = [t]
    altitudes = [h]
    distances = [x]
    velocities = [v0]
    masses = [m]

    for step in range(100000):
        if h <= 0:
            break

        v = np.sqrt(vx**2 + vy**2)
        T, P_atm, rho = calculate_atmosphere(h)

        if t < tb - 0.000001:
            thrust = Isp * m_dot * g0
            dm = m_dot * dt
        else:
            thrust = 0.0
            dm = 0.0

        drag = 0.5 * rho * (v**2) * CD * Af

        ax = ((thrust - drag) * (vx / v)) / m
        ay = ((thrust - drag) * (vy / v)) / m - g0

        x = x + vx * dt
        h = h + vy * dt
        vx = vx + ax * dt
        vy = vy + ay * dt
        m = m - dm
        t = t + dt

        if h > max_h:
            max_h = h

        v_new = np.sqrt(vx**2 + vy**2)

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
        "max_h": max_h,
    }


class AboutWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setObjectName("aboutWindow")
        self.initUI()

    def initUI(self):
        self.setWindowTitle("About Rocket Trajectory")
        self.setGeometry(480, 260, 410, 220)

        heading = QLabel("Rocket Propulsion")
        heading.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")

        description = QLabel(
            "Trajectory simulation assignment interface\n"
            "Interactive plots for altitude, distance, trajectory, velocity, "
            "and rocket mass."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 13px; color: #475569;")

        repository = QLabel(
            '<a href="https://github.com/idone2014-hub/Rcket_Bonus_2">'
            "https://github.com/idone2014-hub/Rcket_Bonus_2</a>"
        )
        repository.setObjectName("repositoryLink")
        repository.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        repository.setOpenExternalLinks(True)
        repository.setStyleSheet("font-size: 12px; color: #3977e8; font-weight: bold;")

        close_button = QPushButton("Close")
        close_button.setObjectName("aboutCloseButton")
        close_button.clicked.connect(self.close_clicked)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(12)
        layout.addWidget(heading)
        layout.addWidget(description)
        layout.addWidget(repository)
        layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def close_clicked(self):
        self.hide()


class RocketTrajectoryWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")
        self.about_window = AboutWindow()

        self.GRAPH_KEYS = ["altitude", "distance", "trajectory", "velocity", "mass"]
        self.GRAPHS = {
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

        self.part_a = calculate_single_step()
        self.results = simulate_trajectory()

        print(f"Part A (t = 0.5 s): Velocity = {self.part_a['v']:.2f} m/s")

        self.initUI()
        self.plot_graph("altitude")

    def initUI(self):
        self.setWindowTitle("Rocket Propulsion | Trajectory Simulator")
        self.resize(1180, 760)

        root = QWidget()
        self.setCentralWidget(root)

        # ----- Sidebar -----
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet("background-color: #0f172a;")

        brand = QLabel("ORBITAL")
        brand.setStyleSheet("color: #ffffff; font-size: 22px; font-weight: bold;")

        subtitle = QLabel("ROCKET TRAJECTORY")
        subtitle.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold;")

        nav_heading = QLabel("VISUALIZATIONS")
        nav_heading.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold;")

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20, 26, 20, 22)
        sidebar_layout.setSpacing(10)
        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addWidget(nav_heading)

        self.navigation_buttons = {}
        for graph_type in self.GRAPH_KEYS:
            graph = self.GRAPHS[graph_type]
            button = QPushButton(graph["button"])
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(self.graph_button_clicked)
            sidebar_layout.addWidget(button)
            self.navigation_buttons[graph_type] = button

        sidebar_layout.addStretch()

        about_button = QPushButton("About this project")
        about_button.setObjectName("aboutButton")
        about_button.clicked.connect(self.show_about_window)
        sidebar_layout.addWidget(about_button)

        sidebar.setLayout(sidebar_layout)

        # ----- Content Area -----
        content = QWidget()
        content.setObjectName("contentArea")
        content.setStyleSheet("background-color: #f4f6fa;")

        page_title = QLabel("Flight analysis")
        page_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a;")

        page_description = QLabel(
            f"Part A (t = 0.5 s): v = {self.part_a['v']:.2f} m/s  |  "
            f"Part B: Max altitude = {self.results['max_h']:.1f} m"
        )
        page_description.setStyleSheet("font-size: 14px; color: #475569; font-weight: bold;")

        chart_box = QWidget()
        chart_box.setStyleSheet(
            "background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;"
        )

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.toolbar = NavigationToolbar2QT(self.canvas, chart_box)
        self.toolbar.setObjectName("plotToolbar")

        chart_layout = QVBoxLayout()
        chart_layout.setContentsMargins(12, 12, 12, 12)
        chart_layout.setSpacing(6)
        chart_layout.addWidget(self.toolbar)
        chart_layout.addWidget(self.canvas, 1)
        chart_box.setLayout(chart_layout)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 26, 30, 28)
        content_layout.setSpacing(18)
        content_layout.addWidget(page_title)
        content_layout.addWidget(page_description)
        content_layout.addWidget(chart_box, 1)
        content.setLayout(content_layout)

        # ----- Root Layout -----
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(sidebar, 1)
        root_layout.addWidget(content, 4)

        root.setLayout(root_layout)

    def graph_button_clicked(self):
        clicked_text = self.sender().text()
        for key in self.GRAPH_KEYS:
            if self.GRAPHS[key]["button"] == clicked_text:
                self.plot_graph(key)

    def plot_graph(self, graph_type):
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

        self.ax.clear()
        self.ax.plot(x_values, y_values, color="#3977e8", linewidth=2.0)
        self.ax.set_title(graph["title"])
        self.ax.set_xlabel(graph["xlabel"])
        self.ax.set_ylabel(graph["ylabel"])
        self.ax.grid(True)
        self.ax.set_xlim(left=0)
        self.ax.set_ylim(bottom=0)
        self.canvas.draw()
        self.toolbar.update()
        self.toolbar.push_current()

        for key in self.GRAPH_KEYS:
            self.navigation_buttons[key].setChecked(key == graph_type)

    def show_about_window(self):
        self.about_window.show()
        self.about_window.raise_()
        self.about_window.activateWindow()

    def closeEvent(self, event):
        self.about_window.close()


if __name__ == "__main__":
    app = QApplication()
    with Path(__file__).with_name("style.qss").open(encoding="utf-8") as stylesheet:
        app.setStyleSheet(stylesheet.read())
    window = RocketTrajectoryWindow()
    window.show()
    app.exec()