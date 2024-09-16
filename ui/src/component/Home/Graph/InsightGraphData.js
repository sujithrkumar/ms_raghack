import React, { useEffect, useState, useRef } from "react";
import neo4j from "neo4j-driver";
import ForceGraph2D from "react-force-graph-2d";

const Neo4jForceGraph = () => {
	const [graphData, setGraphData] = useState({ nodes: [], links: [] });
	const fgRef = useRef();

	// Initialize Neo4j driver
	const driver = neo4j.driver(
		process.env.REACT_APP_NEO4j_DB,
		neo4j.auth.basic(process.env.REACT_APP_USER, process.env.REACT_APP_PASS)
	);

	useEffect(() => {
		const fetchData = async () => {
			const session = driver.session();
			try {
				// Update the Cypher query to return ACTED_IN relationships
				const result = await session.run(
					`MATCH p=(ent : Entity)<-[mention : MENTIONS]-(chunk : Chunk)<-[chunk_of : CHUNK_OF]-(video: VIDEO {video_id :'best_camera_phones_under_20K.mp4'}) RETURN p LIMIT 5`
				);

				const nodes = [];
				const links = [];

				result.records.forEach((record) => {
					const path = record.get("p");

					path.segments.forEach((segment) => {
						const source = segment.start;
						const target = segment.end;
						const relationship = segment.relationship;
						console.log(source, "source");
						console.log(target, "target");

						if (
							!nodes.find(
								(node) => node.id === source.identity.toString()
							)
						) {
							nodes.push({
								id: source.identity.toString(),
								label: source.properties.name,
								...source.properties,
								type: "source"
							});
						}

						if (
							!nodes.find(
								(node) => node.id === target.identity.toString()
							)
						) {
							nodes.push({
								id: target.identity.toString(),
								label: target.properties.video_id,
								...target.properties,
								type: "target"
							});
						}

						// Add the ACTED_IN relationships (links)
						links.push({
							source: source.identity.toString(),
							target: target.identity.toString(),
							label: relationship.type
						});
					});
				});

				setGraphData({ nodes, links });

				// Zoom and fit the graph to the container
				if (fgRef.current) {
					fgRef.current.zoomToFit(200); // Adjusts to fit the nodes within the screen
				}
			} catch (error) {
				console.error("Error fetching data:", error);
			} finally {
				session.close();
			}
		};

		fetchData();

		return () => driver.close();
	}, []);

	return (
		<div>
			<ForceGraph2D
				ref={fgRef}
				graphData={graphData}
				width={1200} // Set a fixed width
				height={500}
				linkDirectionalArrowLength={6}
				linkDirectionalArrowRelPos={1} // Position arrow at the end
				nodeCanvasObjectMode={() => "before"} // Ensures nodes are rendered before text
				nodeVisibility={(node) => node.id !== "0"}
				nodeCanvasObject={(node, ctx, globalScale) => {
					const label = node.label;
					const fontSize = 10 / globalScale; // Increased font size for better visibility
					const radius = 12; // Increased bubble radius

					// Set color based on whether it's a source or target
					ctx.fillStyle =
						node.type === "source" ? "#4cbbe7" : "#f491a2";

					// Draw bubble (circle)
					ctx.beginPath();
					ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
					ctx.fill();

					// Add label text on top of the bubble
					ctx.font = `${fontSize}px Sans-Serif`;
					ctx.fillStyle = "black";

					ctx.fillText(label, node.x, node.y); // Display text on top of the circle
				}}
				enableNodeDrag={true}
				onEngineStop={() => {
					if (fgRef.current) {
						fgRef.current.zoomToFit(100);
					}
				}}
			/>
		</div>
	);
};

export default Neo4jForceGraph;
