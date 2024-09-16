import {
	Alert,
	Box,
	Button,
	Checkbox,
	Paper,
	Snackbar,
	Typography
} from "@mui/material";
import { CustomLoginInputField } from "../CommonInput";
import { useEffect, useState } from "react";
import Person3Icon from "@mui/icons-material/Person3";
import LockIcon from "@mui/icons-material/Lock";
import { useNavigate } from "react-router-dom";

const backgroundImage = window.location.origin + "/assets/images/VIDSAGE.png";
const Login = ({ authenticated, setAuthenticated }) => {
	const [userId, setUserId] = useState("");
	const [password, setPassword] = useState("");
	const navigate = useNavigate();

	const handleLogin = () => {
		if (userId === "admin" && password === "admin@123") {
			setAuthenticated(true);
			navigate("/home");
		} else {
			setAuthenticated(false);
		}

		// setIsLoggedIn(true);

		// oktaAuth.signInWithRedirect({ originalUri: "/" });
	};

	const handleUserId = (e) => {
		setUserId(e.target.value);
	};
	const handlePassword = (e) => {
		setPassword(e.target.value);
	};

	// useEffect(() => {
	// 	if (authState?.isAuthenticated) {
	// 		navigate("/home");
	// 	}
	// }, []);
	return (
		<Box
			sx={{
				backgroundImage: `url(${backgroundImage})`,
				backgroundSize: "cover",
				backgroundPosition: "center",
				backgroundRepeat: "no-repeat",
				minHeight: "100vh"
			}}
		>
			<Box
				sx={{
					paddingTop: "12%",
					display: "flex",
					paddingRight: "3%",
					justifyContent: "flex-end"
				}}
			>
				<Paper
					elevation={3}
					sx={{
						width: "24%",
						height: "420px",
						padding: "1%",
						borderRadius: "20px"
					}}
				>
					{/* <Snackbar
						open={authenticated}
						autoHideDuration={3000}
						onClose={() => setAuthenticated(false)}
						anchorOrigin={{
							vertical: "bottom",
							horizontal: "center"
						}}
					>
						<Alert
							onClose={() => setAuthenticated(false)}
							severity="error"
							sx={{ width: "100%" }}
						>
							Bad Credentials
						</Alert>
					</Snackbar> */}
					<Box
						sx={{
							display: "flex",
							justifyContent: "center",
							marginTop: "45px"
						}}
					>
						<Typography fontSize="32px" fontWeight="bold">
							Sign In
						</Typography>
					</Box>
					<Box
						sx={{
							display: "flex",
							justifyContent: "center",
							marginTop: "30px",
							fontSize: "20px !important",
							alignItems: "center",
							gap: "5px"
						}}
					>
						<Person3Icon fontSize="large" />
						<CustomLoginInputField
							value={userId}
							variant="standard"
							placeholder="User Id"
							onChange={handleUserId}
							autoFocus
						/>
					</Box>
					<Box
						sx={{
							display: "flex",
							justifyContent: "center",
							marginTop: "50px",
							fontSize: "20px !important",
							alignItems: "center",
							gap: "5px"
						}}
					>
						<LockIcon fontSize="large" />
						<CustomLoginInputField
							value={password}
							variant="standard"
							type="password"
							placeholder="Password"
							onChange={handlePassword}
							autoFocus
						/>
					</Box>
					<Box
						sx={{
							display: "flex",
							justifyContent: "center",
							marginTop: "20px"
						}}
					>
						<Box
							sx={{
								width: "90%",
								display: "flex",
								alignItems: "center",
								justifyContent: "space-between"
							}}
						>
							<Box>
								<Typography
									fontSize="18px"
									fontFamily="bold"
									sx={{
										color: "#4858a6",
										":hover": {
											cursor: "pointer"
										}
									}}
									// onClick={() =>
									// 	setOpenForgotPasswordDialog(true)
									// }
								>
									Forgot Password?
								</Typography>
							</Box>
						</Box>
					</Box>
					<Box
						sx={{
							display: "flex",
							justifyContent: "center",
							marginTop: "36px"
						}}
					>
						<Button
							variant="contained"
							sx={{
								width: "90%",
								height: "50px",
								textTransform: "none"
							}}
							onClick={handleLogin}
						>
							<Typography>Login</Typography>
						</Button>
					</Box>

					{/* <Box
						sx={{
							display: "flex",
							justifyContent: "center",
							marginTop: "15px"
						}}
					>
						<Typography
							sx={{ color: "#6e6e6e" }}
							fontFamily="bold"
							fontSize="18px"
						>
							Don't have an account?Sign up now
						</Typography>
					</Box> */}
				</Paper>
			</Box>
		</Box>
	);
};
export default Login;
