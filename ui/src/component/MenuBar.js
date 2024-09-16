import { Box, Paper } from "@mui/material";
import SettingsIcon from "@mui/icons-material/Settings";
import NotificationsNoneIcon from "@mui/icons-material/NotificationsNone";
import LogoutIcon from "@mui/icons-material/Logout";
import { useNavigate } from "react-router-dom";
import { Height } from "@mui/icons-material";

// import LOGO from "./Asset/Image/logo.jpg";

const MenuBar = ({ setAuthenticated }) => {
	const navigate = useNavigate();
	const handleLogout = () => {
		setAuthenticated(false);
		navigate("/");
	};
	return (
		<Box>
			<Paper
				sx={{
					display: "flex",
					padding: ".5% 1% .5% 1%",
					alignItems: "center",
					justifyContent: "space-between"
				}}
				elevation={3}
			>
				<Box>
					<img
						src={
							window.location.origin +
							"/assets/images/c5i_logo.png"
						}
						alt="logo"
						style={{ width: "35px", height: "35px" }}
					/>
				</Box>
				<Box
					sx={{
						width: "10%",
						display: "flex",
						alignItems: "center",
						justifyContent: "space-between"
					}}
				>
					<NotificationsNoneIcon
						fontSize="large"
						sx={{ color: "#5f5f5f" }}
					/>
					<SettingsIcon fontSize="large" sx={{ color: "#5f5f5f" }} />
					<LogoutIcon
						fontSize="large"
						sx={{
							color: "#5f5f5f",
							":hover": {
								cursor: "pointer"
							}
						}}
						onClick={handleLogout}
					/>
				</Box>
			</Paper>
			<Box>
				<img
					src={window.location.origin + "/assets/images/VIDSAGE.png"}
					alt="logo"
					style={{
						width: "100%",
						height: "180px",
						objectFit: "fill",
						borderRadius: "10px"
					}}
				/>
			</Box>
		</Box>
	);
};
export default MenuBar;
