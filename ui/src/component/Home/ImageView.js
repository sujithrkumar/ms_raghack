import { Box, CardMedia, Paper, Typography } from "@mui/material";

import { useEffect, useState } from "react";

const data = [
	{
		imageUrl: "/assets/images/algebra.jpg",
		header: "Algebra "
	},
	{
		imageUrl: "/assets/images/deep_learning.jpg",
		header: "Deep Learning"
	},
	{
		imageUrl: "/assets/images/computer_vision.jpg",
		header: "Computer Vision"
	}
];
const ImageView = ({ searchResult }) => {
	const [images, setImages] = useState([]);

	useEffect(() => {
		searchResult?.search_results.map((item) => {
			setImages([...images, ...item.keyframe_blob_paths]);
		});
	}, [searchResult]);

	return (
		<Box>
			<Box>
				{images?.slice(0, 10).map((item) => (
					<Paper
						elevation={3}
						sx={{
							padding: "10px 15px 10px 15px",
							display: "inline-block",
							margin: "20px",
							width: "20%",
							borderRadius: "20px 20px 0px 0px",
							borderBottom: "5px solid transparent",
							borderImage:
								"linear-gradient(to left, #e07269 0%, #7c91dd)",
							borderImageSlice: 4
						}}
					>
						<Box>
							<img
								src={item}
								alt="img"
								controls
								style={{
									width: "100%",
									height: "180px"
								}}
							/>
						</Box>
						<Box sx={{ marginBottom: "8px" }}>
							<Typography
								fontWeight="bold"
								sx={{ fontSize: "20px", color: "#4858a6" }}
							>
								{item.header}
							</Typography>
						</Box>
					</Paper>
				))}
			</Box>
		</Box>
	);
};
export default ImageView;
