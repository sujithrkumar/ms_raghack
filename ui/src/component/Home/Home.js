import { Box } from "@mui/material";

import { useState } from "react";

import TopicList from "./TopicList";

const Home = () => {
	const [searchItem, setSearchItem] = useState(false);
	const handleSearch = () => {
		setSearchItem(!searchItem);
	};
	return (
		<Box>
			<TopicList />
		</Box>
	);
};
export default Home;
