"""PySide6 interface for a rocket-propulsion trajectory assignment.

The calculation functions in this module are intentional placeholders. Replace
their TODO sections with the assignment's physics and numerical methods.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

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


def calculate_atmosphere(h: float) -> tuple[float, float]:
    """Return placeholder temperature and pressure for altitude ``h``.

    TODO: Implement the assignment's atmospheric model separately for the
    troposphere below 11 km and the regime at/above 11 km.
    """
    if h < 11_000:
        # TODO: Replace with the below-11-km atmospheric equations.
        temperature, pressure = 0.0, 0.0
    else:
        # TODO: Replace with the at/above-11-km atmospheric equations.
        temperature, pressure = 0.0, 0.0
    return temperature, pressure


def calculate_single_step(
    h0: float = 2000.0,
    Isp: float = 260.0,
    theta: float = 50.0,
    m_dot: float = 15.0,
    CD: float = 0.2,
    m0: float = 200.0,
    Af: float = 0.1,
    M: float = 1.0,
    tb: float = 7.0,
    dt: float = 0.5,
) -> dict[str, Any]:
    """Placeholder for Part A's single calculation at ``t = 0.5 s``.

    The defaults are the assignment's initial conditions. TODO: Implement one
    time-step calculation using the applicable propulsion and flight equations.
    """
    # TODO: Calculate the state at dt from h0, Isp, theta, m_dot, CD, m0,
    # Af, M, and tb. These values deliberately do not model rocket physics.
    return {
        "t": dt,
        "h": h0,
        "x": 0.0,
        "v": 0.0,
        "m": m0,
    }


def simulate_trajectory(
    h0: float = 2000.0,
    Isp: float = 260.0,
    theta: float = 50.0,
    m_dot: float = 15.0,
    CD: float = 0.2,
    m0: float = 200.0,
    Af: float = 0.1,
    M: float = 1.0,
    tb: float = 7.0,
    dt: float = 0.01,
    t_final: float = 30.0,
) -> dict[str, np.ndarray]:
    """Return placeholder time-series arrays for Part B.

    TODO: Implement the numerical integration, applying powered-flight
    equations until burnout at ``tb`` and coast/descent equations afterward.
    The loop below only demonstrates the requested time and burn/coast
    structure; its held-constant state values are not a physical simulation.
    """
    times = [0.0]
    altitudes = [h0]
    distances = [0.0]
    velocities = [0.0]
    masses = [m0]

    t = 0.0
    while t < t_final:
        if t < tb:
            # TODO: Update the state during engine burn.
            pass
        else:
            # TODO: Update the state after burnout.
            pass

        t = min(t + dt, t_final)
        times.append(t)
        # TODO: Append the newly calculated state instead of these placeholders.
        altitudes.append(h0)
        distances.append(0.0)
        velocities.append(0.0)
        masses.append(m0)

    return {
        "t": np.asarray(times),
        "h": np.asarray(altitudes),
        "x": np.asarray(distances),
        "v": np.asarray(velocities),
        "m": np.asarray(masses),
    }


class AboutDialog(QDialog):
    """Project information dialog with an external repository link."""

    def __init__(self, parent: QWidget | None = None) -> None:
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
    """Main window containing graph navigation and an interactive plot."""

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
            "title": "Rocket Trajectory",
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

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Rocket Propulsion | Trajectory Simulator")
        self.resize(1180, 760)
        self.setMinimumSize(900, 600)

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

        self.navigation_buttons: dict[str, QPushButton] = {}
        for graph_type, graph in self.GRAPHS.items():
            button = QPushButton(graph["button"])
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setMinimumHeight(44)
            button.clicked.connect(
                lambda checked=False, selected=graph_type: self.plot_temporary_graph(
                    selected
                )
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
            "Explore the simulated rocket flight using the graph controls."
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

        self.plot_temporary_graph("altitude")

    def plot_temporary_graph(self, graph_type: str) -> None:
        """Draw temporary NumPy data for the selected graph.

        Replace this method's sample data and plotting code with the real
        simulation results when the physics functions are implemented.
        """
        graph = self.GRAPHS[graph_type]
        sample_time = np.linspace(0.0, 10.0, 101)

        if graph_type == "altitude":
            x_values, y_values = sample_time, 2000.0 + 120.0 * sample_time
        elif graph_type == "distance":
            x_values, y_values = sample_time, 35.0 * sample_time
        elif graph_type == "trajectory":
            x_values = 35.0 * sample_time
            y_values = 2000.0 + 120.0 * sample_time
        elif graph_type == "velocity":
            x_values, y_values = sample_time, 40.0 + 8.0 * sample_time
        else:
            x_values, y_values = sample_time, 200.0 - 15.0 * sample_time

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

    def show_about_dialog(self) -> None:
        """Open the project information dialog."""
        AboutDialog(self).exec()


def main() -> int:
    """Start the application and load its adjacent Qt stylesheet."""
    app = QApplication(sys.argv)
    stylesheet_path = Path(__file__).with_name("style.qss")
    if not stylesheet_path.is_file():
        raise FileNotFoundError(f"Stylesheet not found: {stylesheet_path}")
    app.setStyleSheet(stylesheet_path.read_text(encoding="utf-8"))

    window = RocketTrajectoryWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
