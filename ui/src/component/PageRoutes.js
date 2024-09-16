import { Routes, Route } from "react-router-dom";
import Login from "./Login/Login";
import Home from "./Home/Home";
import TopicMaterial from "./Home/TopicMaterial";

const PageRoutes = ({ authenticated, setAuthenticated }) => {
	return (
		<Routes>
			<Route
				path="/"
				exact
				element={
					<Login
						authenticated={authenticated}
						setAuthenticated={setAuthenticated}
					/>
				}
			/>
			<Route path="/home" exact element={<Home />} />
			<Route path="/home/:path" element={<TopicMaterial />} />

			<Route path="*" element={<Login />} />
		</Routes>
	);
};
export default PageRoutes;
