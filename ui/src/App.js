import { Box, Button, Typography } from "@mui/material";

import { useState } from "react";
import PageRoutes from "./component/PageRoutes";
import MenuBar from "./component/MenuBar";

function App() {
	const [authenticated, setAuthenticated] = useState(false);
	return (
		<Box>
			{authenticated && <MenuBar setAuthenticated={setAuthenticated} />}
			<Box>
				<PageRoutes
					authenticated={authenticated}
					setAuthenticated={setAuthenticated}
				/>
			</Box>
			{authenticated && (
				<Box
					sx={{
						width: "100%",
						background: "#64b9ed",

						position: "absolute"
					}}
				>
					<Box sx={{ padding: "10px 0px 10px 40px" }}>
						<Typography fontSize="13px" sx={{ color: "white" }}>
							© 2024 c5i, All Rights Reserved.
						</Typography>
					</Box>
				</Box>
			)}
		</Box>
	);
}

export default App;
