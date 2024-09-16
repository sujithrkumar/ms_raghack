import { Box, CardMedia, Paper, Typography } from "@mui/material";
import { useEffect, useRef } from "react";

const convertTimeToSeconds = (time) => {
	const [hours, minutes, seconds] = time.split(":");
	const [sec, ms] = seconds.split(".");
	return (
		parseInt(hours) * 3600 +
		parseInt(minutes) * 60 +
		parseInt(sec) +
		(ms ? parseFloat(`0.${ms}`) : 0)
	);
};

const FilterData = ({ searchResult }) => {
	const videoRefs = useRef([]);

	useEffect(() => {
		videoRefs.current.forEach((video, index) => {
			if (video) {
				const startTime = convertTimeToSeconds(
					searchResult?.search_results[index].start_time
				);
				video.onloadedmetadata = () => {
					video.currentTime = startTime;
				};
			}
		});
	}, [searchResult]);

	return (
		<Box sx={{ display: "flex" }}>
			<Box sx={{ width: "70%" }}>
				{searchResult?.search_results.map((item, index) => (
					<Paper
						key={index}
						elevation={3}
						sx={{
							padding: "10px 15px 10px 15px",
							display: "inline-block",
							margin: "5px",
							width: "45%",
							borderRadius: "20px 20px 0px 0px",
							borderBottom: "5px solid transparent",
							borderImage:
								"linear-gradient(to left, #e07269 0%, #7c91dd)",
							borderImageSlice: 4
						}}
					>
						<Box>
							<CardMedia
								component="video"
								controls
								ref={(el) => (videoRefs.current[index] = el)}
								src={
									window.location.origin +
									"/assets/video/" +
									item.video_path
								}
								style={{
									width: "100%",
									height: "180px"
								}}
							/>
						</Box>
						<Box sx={{ marginBottom: "8px" }}>
							<Typography
								fontWeight="bold"
								sx={{ fontSize: "15px", color: "#4858a6" }}
							>
								{item.video_path}
							</Typography>
						</Box>
					</Paper>
				))}
			</Box>
			<Box
				sx={{
					width: "30%",
					padding: "10px",
					height: "70vh",
					overflow: "auto",
					borderLeft: "1px solid #e6e6e6"
				}}
			>
				<Box sx={{ display: "flex", justifyContent: "center" }}>
					<Typography fontSize="30px" color="info.dark">
						Summary
					</Typography>
				</Box>
				<Box>
					<Typography
						variant="textSizeParagraph"
						dangerouslySetInnerHTML={{
							__html: `${searchResult?.answer} `
						}}
					/>
				</Box>
			</Box>
		</Box>
	);
};
export default FilterData;
