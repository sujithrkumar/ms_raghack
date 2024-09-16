import * as React from "react";
import PropTypes from "prop-types";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Box from "@mui/material/Box";
import VideoView from "./VideoView";
import ImageView from "./ImageView";

import Neo4jForceGraph from "./Graph/InsightGraphData";

function CustomTabPanel(props) {
	const { children, value, index, ...other } = props;

	return (
		<div
			role="tabpanel"
			hidden={value !== index}
			id={`simple-tabpanel-${index}`}
			aria-labelledby={`simple-tab-${index}`}
			{...other}
		>
			{value === index && <Box sx={{ p: 3 }}>{children}</Box>}
		</div>
	);
}

CustomTabPanel.propTypes = {
	children: PropTypes.node,
	index: PropTypes.number.isRequired,
	value: PropTypes.number.isRequired
};

function a11yProps(index) {
	return {
		id: `simple-tab-${index}`,
		"aria-controls": `simple-tabpanel-${index}`
	};
}

export default function SearchContent({ searchResult }) {
	const [value, setValue] = React.useState(0);

	const handleChange = (event, newValue) => {
		setValue(newValue);
	};

	return (
		<Box sx={{ width: "100%" }}>
			<Box
				sx={{
					borderBottom: 1,
					borderColor: "divider",
					backgroundColor: "#e6e6e6"
				}}
			>
				<Tabs
					value={value}
					onChange={handleChange}
					aria-label="basic tabs example"
				>
					<Tab label="Video" {...a11yProps(0)} />
					<Tab label="Images" {...a11yProps(1)} />
					<Tab label="Insight" {...a11yProps(2)} />
				</Tabs>
			</Box>
			<CustomTabPanel value={value} index={0}>
				<VideoView searchResult={searchResult} />
			</CustomTabPanel>
			<CustomTabPanel value={value} index={1}>
				<ImageView searchResult={searchResult} />
			</CustomTabPanel>
			<CustomTabPanel value={value} index={2}>
				<Neo4jForceGraph />
			</CustomTabPanel>
		</Box>
	);
}
