import { Box, Button, Divider, Paper, Typography } from "@mui/material";

import { useNavigate } from "react-router-dom";
const data = [
	{
		img: "/assets/images/Best_Camera_Phones.webp",
		route: "sell_phone",
		header: "Best Sellphone under 20k"
	},
	{
		img: "/assets/images/xbox.webp",
		route: "xbox_research",
		header: "XBOX Research"
	},
	{
		img: "/assets/images/gaming.jpg",
		route: "xbox_research",
		header: "Gaming Laptop under 50k"
	}
];
const TopicList = () => {
	const navigate = useNavigate();
	const handleContinue = (routePath) => {
		navigate(`/home/${routePath}`);
	};
	return (
		<Box sx={{ padding: "1% 3% 2% 3%", minHeight: "60vh" }}>
			<Box
				sx={{
					display: "flex",
					justifyContent: "space-between",
					alignItems: "center",
					marginBottom: "5px"
				}}
			>
				<Box>
					<Typography
						fontWeight="bold"
						sx={{ fontSize: "20px", color: "#4858a6" }}
					>
						Explore
					</Typography>
				</Box>
			</Box>
			<Divider />
			<Box>
				{data.map((item) => (
					<Paper
						sx={{
							padding: "10px 15px 10px 15px",
							display: "inline-block",
							margin: "20px",
							width: "28%",
							borderRadius: "20px 20px 0px 0px",
							borderBottom: "5px solid transparent",
							borderImage:
								"linear-gradient(to left, #e07269 0%, #7c91dd)",
							borderImageSlice: 4
						}}
					>
						<Box>
							<img
								src={window.location.origin + item.img}
								alt="logo"
								style={{
									width: "100%",
									height: "200px",
									objectFit: "fill"
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

						<Box
							sx={{
								justifyContent: "flex-end",
								display: "flex"
							}}
						>
							<Button
								color="warning"
								sx={{ height: "30px", width: "130px" }}
								onClick={() => handleContinue(item.route)}
							>
								Get Started
							</Button>
						</Box>
					</Paper>
				))}
			</Box>
		</Box>
	);
};
export default TopicList;
