// Diamond Model
module diamond() {
    color("white", 0.9) // Add a slight transparency for visualization
        union() {
            // Top half of the diamond
            scale([1, 1, 1.5]) // Stretch vertically for a diamond proportion
                polyhedron(
                    points=[
                        [0, 0, 1],     // Topmost tip
                        [1, 0, 0],     // Points at the base
                        [-1, 0, 0],
                        [0, 1, 0],
                        [0, -1, 0],
                        [0, 0, -1]     // Bottommost tip
                    ],
                    faces=[
                        [0, 1, 3], // Top pyramid faces
                        [0, 3, 2],
                        [0, 2, 4],
                        [0, 4, 1],

                        [5, 3, 1], // Bottom pyramid faces
                        [5, 2, 3],
                        [5, 4, 2],
                        [5, 1, 4]
                    ]
                );
        }
}

// Call the diamond module
diamond();