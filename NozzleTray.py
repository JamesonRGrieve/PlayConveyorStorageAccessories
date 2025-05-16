import cadquery

clearance = 0.2


class prism_rect:
    def __init__(self, length, width, height):
        self.length = length
        self.width = width
        self.height = height

    def render(self):
        return self.render_from(0, 0, 0)

    def render_from(self, x, y, z):
        return (
            cadquery.Workplane("XY")
            .box(self.length, self.width, self.height)
            .translate(
                [(self.length / 2) + x, (self.width / 2) + y, (self.height / 2) + z]
            )
        )


class nozzle_tray:
    def __init__(
        self,
        tier,
        handle_width=6,
        handle_spacing_outer=4,
        handle_chamfer=0.4,
        handle_depth=3,
        height=10,
    ):
        self.tier = tier
        self.handle_width = handle_width
        self.handle_spacing_outer = handle_spacing_outer
        self.handle_chamfer = handle_chamfer
        self.height = height
        self.handle_depth = handle_depth
        self.handle_spacing_inner = (
            (41 - self.handle_spacing_outer * 2) - (self.handle_width * 4)
        ) / 3

    def render(self):
        tray = (
            prism_rect(41, 46, 10)
            .render_from(0, 0, self.tier * 10)
            .edges("|Z")
            .chamfer(0.6)
        )
        # Holes for Nozzle Threads
        tray = (
            tray.faces(">Z")
            .workplane()
            .center(41 / 2, 51 / 2)
            .rarray(38 / 4, 38 / 4, 4, 4)
            .hole(6.2, 7.5)
        )
        # Holes for Nozzle Tips
        tray = (
            tray.faces("<Z")
            .workplane()
            .rarray(38 / 4, 38 / 4, 4, 4)
            .hole(8.2, 5)
            .faces("<<Z[1]")
            .edges("<Z")
            .chamfer(0.999)
        )
        # Handle
        handle = (
            prism_rect(self.handle_width, self.handle_depth, (40 - self.tier * 10) + 5)
            .render_from(
                self.handle_spacing_outer
                + self.tier * (self.handle_width + self.handle_spacing_inner),
                0,
                self.tier * 10,
            )
            .edges(">Y")
            .edges("|Z")
            .chamfer(self.handle_chamfer)
            # .faces(">Y")
            # .extrude(5)
        )
        triangle_grip = (
            handle.faces("<X")  # Select the top face (assuming Z is up)
            .workplane(offset=-0.4)
            .moveTo(-3, 40)  # Start at the left edge
            .lineTo(-6, 45)  # Draw to the peak of the triangle
            .lineTo(-3, 45)  # Draw to the right edge
            .close()
            .extrude(-5.2)  # Extrude the triangle
        )

        handle = handle.union(triangle_grip)
        text_feature = (
            handle.faces(">Z")  # Select the top face
            .workplane()
            .center(
                self.handle_spacing_outer
                + self.tier * (self.handle_width + self.handle_spacing_inner)
                + 3,
                1.5,
            )  # Position text in center of face
            .text(
                str(
                    round(0.2 * (self.tier + 1 if self.tier < 1 else self.tier + 2), 2)
                ),
                3,
                -0.6,
                cut=False,
                kind="bold",
            )  # Larger text, less depth, embossed
        )

        # Add the text to the handle
        handle = handle.cut(text_feature)  # For raised text
        # Handle Holes
        tray = tray.union(handle)
        for i in range(self.tier):
            tray = tray.cut(
                prism_rect(
                    self.handle_width + (2 * clearance),
                    self.handle_depth + clearance,
                    (4 * self.height - (i * self.height)),
                )
                .render_from(
                    (
                        self.handle_spacing_outer
                        + i * (self.handle_width + self.handle_spacing_inner)
                    )
                    - clearance,
                    0,
                    (i * self.height),
                )
                .edges(">Y")
                .edges("|Z")
                .chamfer(self.handle_chamfer + clearance)
            )
        return tray


bottom_tray = nozzle_tray(0).render()
second_tray = nozzle_tray(1).render()
third_tray = nozzle_tray(2).render()
top_tray = nozzle_tray(3).render()

show_object(bottom_tray)
show_object(second_tray)
show_object(third_tray)
show_object(top_tray)
