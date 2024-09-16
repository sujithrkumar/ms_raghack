import {
	Box,
	Button,
	CardMedia,
	Chip,
	Divider,
	IconButton,
	InputBase,
	LinearProgress,
	Paper,
	Stack,
	TextField,
	Typography
} from "@mui/material";
import HomeIcon from "@mui/icons-material/Home";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import SearchIcon from "@mui/icons-material/Search";
import SearchContent from "./SearchContent";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import FilterData from "./FilterData";
import PermMediaIcon from "@mui/icons-material/PermMedia";
import DeleteIcon from "@mui/icons-material/Delete";

const StudyMaterialData = [
	{
		type: "sell_phone",
		topic: "Best Sellphone under 20k",
		subTopics: [
			"Camera Performance",
			"Software Experience",
			"Battery Life",
			"Design & Build"
		],
		summary:
			"<ul><li>The Realme 12 + 5G is highlighted for its impressive camera capabilities and strong performance with the Diamond City 7050 chipset.</li><li>Other notable models include the Redmi 13 5G, Moto G85, and Poco X6, which are praised for their design and battery life.</li><li>Common themes across the reviews include discussions on camera quality, display performance, and software experiences.</li><li>Many smartphones face issues with bloatware, impacting user experience.</li><li>Speakers recommend different models based on specific needs such as gaming or photography.</li><li>The overall sentiment is positive, indicating that these budget smartphones offer good value for their price.</li></ul><p>In conclusion, viewers are encouraged to consider their personal preferences while choosing among these budget smartphones to make an informed decision in the competitive market.</p>",

		topics: [
			"Realme 12 + 5 G",
			"Camera Features",
			"Performance Benchmarks",
			"Display Quality",
			"Design",
			"Software Updates",
			"Smartphones",
			"Realme P1",
			"Phone Features",
			"Battery Life",
			"Redmi 13 5G",
			"CMF Phone One",
			"Motorola G-85 5G",
			"Budget Phones"
		],

		features: [
			"Sony Camera With OIS",
			"Super Wires For Video Stabilization",
			"Diamond City 7050 Chipset",
			"6.6 Inch Full HD Display",
			"120 Hertz Refresh Rate",
			"IP 54 Rating",
			"Android 14 With Realme UI 5.0",
			"50 MP Main Camera",
			"8 MP Ultra-Wide Camera",
			"2 MP Macro Camera",
			"2 Years OS Updates",
			"3 Years Security Updates",
			"45V Charger",
			"Screen Protector",
			"Case",
			"Headphone Jack",
			"Stereo Speakers",
			"5000mAh Battery",
			"120Hz AMOLED Display",
			"HDR Support",
			"Removable Back Plates",
			"Snapdragon 7300 Processor",
			"108-Megapixel Main Camera",
			"Latest Android 14",
			"5030 mAh Battery",
			"33 Watt Charging",
			"Snapdragon 4 Gen. 2 Processor"
		],

		material: [
			{
				videoUrl: "/assets/video/best_camera_phones_under_20K.mp4",
				videoHeader: "Best Camera under 20K"
			},
			{
				videoUrl: "/assets/video/best_phones_under_15K.mp4",
				videoHeader: "Best Phone under 15k"
			},
			{
				videoUrl: "/assets/video/best_smartphone_to_get_in_budget.mp4",
				videoHeader: "Best smartphone to get in budget"
			},
			{
				videoUrl: "/assets/video/the_best_phones_under_20K.mp4",
				videoHeader: "Best Phone under 20k"
			},
			{
				videoUrl: "/assets/video/top_5_best_phones_under_20K.mp4",
				videoHeader: "Top 5 smartphone under 20k"
			}
		]
	},

	{
		type: "xbox_research",
		topic: "XBOX Research ",
		topic: "XBOX top research",
		subTopics: ["Camera Features", "Battery Life", "Budget Phones"],
		summary:
			"The videos provide insights into various smartphones in the budget segment, focusing on their features, performance, and overall value. The Realme 12 + 5 G is highlighted for its impressive camera with a Sony sensor, robust performance, and premium design, making it a strong contender under 20,000. The Realme P1 is recommended for under 15K, praised for its practical features including a 45V charger and good display quality, despite minor drawbacks. The discussion also covers the Redmi 13 5G, noted for its 108-megapixel camera and solid performance, while suggesting the Motorola G-85 5G as a premium option. Overall, the videos emphasize the importance of balancing features, performance, and cost in choosing budget smartphones.",
		topics: [
			"Realme 12 + 5 G",
			"Camera Features",
			"Performance Benchmarks",
			"Display Quality",
			"Design",
			"Software Updates",
			"Smartphones",
			"Realme P1",
			"Phone Features",
			"Battery Life",
			"Redmi 13 5G",
			"CMF Phone One",
			"Motorola G-85 5G",
			"Budget Phones"
		],

		features: [
			"Sony Camera With OIS",
			"Super Wires For Video Stabilization",
			"Diamond City 7050 Chipset",
			"6.6 Inch Full HD Display",
			"120 Hertz Refresh Rate",
			"IP 54 Rating",
			"Android 14 With Realme UI 5.0",
			"50 MP Main Camera",
			"8 MP Ultra-Wide Camera",
			"2 MP Macro Camera",
			"2 Years OS Updates",
			"3 Years Security Updates",
			"45V Charger",
			"Screen Protector",
			"Case",
			"Headphone Jack",
			"Stereo Speakers",
			"5000mAh Battery",
			"120Hz AMOLED Display",
			"HDR Support",
			"Removable Back Plates",
			"Snapdragon 7300 Processor",
			"108-Megapixel Main Camera",
			"Latest Android 14",
			"5030 mAh Battery",
			"33 Watt Charging",
			"Snapdragon 4 Gen. 2 Processor"
		],

		material: [
			{
				videoUrl: "/assets/video/best_camera_phones_under_20K.mp4",
				videoHeader: "Best Camera under 20K"
			},
			{
				videoUrl: "/assets/video/best_phones_under_15K.mp4",
				videoHeader: "Best Phone under 15k"
			},
			{
				videoUrl: "/assets/video/best_smartphone_to_get_in_budget.mp4",
				videoHeader: "Best smartphone to get in budget"
			},
			{
				videoUrl: "/assets/video/the_best_phones_under_20K.mp4",
				videoHeader: "Best Phone under 20k"
			},
			{
				videoUrl: "/assets/video/top_5_best_phones_under_20K.mp4",
				videoHeader: "Top 5 smartphone under 20k"
			}
		]
	}
];
const TopicMaterial = () => {
	const [selectedTopic, setSelectedTopic] = useState();
	const navigate = useNavigate();

	const [studyData, setStudyData] = useState([]);
	const [material, setMaterial] = useState([]);
	const [progress, setProgress] = useState(false);
	const location = useLocation();
	const [searchItem, setSearchItem] = useState(false);
	const [searchResult, setSearchResult] = useState();
	const [searchText, setSearchText] = useState();
	const [subTopicData, setSubTopicData] = useState();
	const [selectedImage, setSelectedImage] = useState(null);

	const handleFileSelect = async (event) => {
		const file = event.target.files[0];
		setSelectedImage(URL.createObjectURL(file));

		searchByImage(file).then((res) => {
			setSearchItem(true);
			setSearchResult(res);
		});
	};

	const handleSelectTopic = (item) => {
		setSelectedTopic(item);
		getSearchItem(item).then((res) => {
			setSubTopicData(res);
		});
	};
	const handleSearchChange = (e) => {
		setSearchText(e.target.value);
	};
	const getSearchItem = async (searchitem) => {
		setProgress(true);
		try {
			const myHeaders = new Headers();
			myHeaders.append("accept", "application/json");

			const requestOptions = {
				method: "POST",
				headers: myHeaders,
				redirect: "follow"
			};
			let response = await fetch(
				"http://3.6.21.71:8500/raghack/api/v1/search-text?query=" +
					encodeURIComponent(searchitem),
				requestOptions
			);
			const result = await response.json();
			if (response.ok) {
				setProgress(false);
				return result;
			} else {
				setProgress(false);
				console.log("something went wrong");
			}
		} catch (error) {
			setProgress(false);
			console.log(error);
		}
	};
	const searchByImage = async (file) => {
		setProgress(true);
		const formData = new FormData();
		formData.append("file", file);

		try {
			const response = await fetch(
				"http://3.6.21.71:8500/raghack/api/v1/search-image",
				{
					method: "POST",
					body: formData
				}
			);
			const result = await response.json();

			if (response.ok) {
				setProgress(false);
				return result;
			} else {
				setProgress(false);
				throw new Error("Failed to search file");
			}
		} catch (error) {
			setProgress(false);

			throw error;
		}
	};
	const handleSearch = () => {
		setSearchItem(true);
		getSearchItem(searchText).then((res) => {
			setSearchResult(res);
		});
	};

	useEffect(() => {
		const filterData = StudyMaterialData.filter(
			(item) =>
				item.type.toUpperCase() ===
				location.pathname.split("/").pop().toUpperCase()
		);
		if (filterData) {
			setStudyData(filterData);
			setMaterial(filterData[0]?.material);
		}
		// console.log(filterData);
	}, [location.pathname.split("/").pop()]);

	return (
		<Box sx={{ minHeight: "70vh" }}>
			<Box sx={{ padding: "1% 3% 2% 3%" }}>
				<Box
					sx={{
						display: "flex",
						justifyContent: "space-between",
						alignItems: "center",
						marginBottom: "5px"
					}}
				>
					<Box>
						{searchItem && (
							<ArrowBackIcon
								color="error"
								onClick={() => {
									setSearchItem(false);
									setSearchText("");
									setSearchResult("");
								}}
							/>
						)}

						<Typography
							fontWeight="bold"
							sx={{ fontSize: "20px", color: "#4858a6" }}
						>
							{searchItem ? "Search Result" : "Explore "}
						</Typography>
					</Box>
					<Box
						sx={{
							width: "30%"
						}}
					>
						<TextField
							sx={{ ml: 1, flex: 1, width: "100%" }}
							value={searchText}
							size="small"
							onChange={handleSearchChange}
							placeholder="Search"
							InputProps={{
								endAdornment: (
									<IconButton onClick={handleSearch}>
										<SearchIcon />
									</IconButton>
								),
								startAdornment: (
									<>
										<input
											accept="image/*"
											type="file"
											style={{ display: "none" }}
											id="icon-button-file"
											onChange={handleFileSelect}
										/>
										<label htmlFor="icon-button-file">
											<IconButton
												component="span"
												sx={{ marginRight: "10px" }}
											>
												<PermMediaIcon />
											</IconButton>
										</label>
										{selectedImage && (
											<Box
												sx={{
													display: "flex",
													alignItems: "center"
												}}
											>
												<img
													src={selectedImage}
													alt="Selected"
													style={{
														width: 44,
														height: 44,
														objectFit: "cover",
														borderRadius: "4px"
													}}
												/>
												<IconButton
													onClick={() =>
														setSelectedImage("")
													}
													sx={{ padding: 0 }}
												>
													<DeleteIcon
														sx={{ fontSize: 20 }}
													/>
												</IconButton>
											</Box>
										)}
									</>
								)
							}}
						/>
					</Box>
				</Box>
				<Divider />
				{progress && <LinearProgress color="success" />}
				{searchItem ? (
					<SearchContent searchResult={searchResult} />
				) : (
					<>
						<Box
							sx={{
								display: "flex",
								background: "#e5e5e5",

								alignItems: "center",
								marginBottom: "5px",
								borderRadius: "10px",
								gap: "3%",
								alignItems: "center"
							}}
						>
							<Box
								sx={{
									width: "8%",
									padding: "10px 10px 10px 10px",
									borderRadius: "0% 30% 30% 0%",
									background: "#4858a6",
									display: "flex",
									gap: "10%",
									alignItems: "center",
									":hover": {
										cursor: "pointer"
									}
								}}
								onClick={() => navigate("/home")}
							>
								<HomeIcon sx={{ color: "white" }} />
								<Typography
									fontWeight="bold"
									sx={{ fontSize: "18px", color: "white" }}
								>
									Home
								</Typography>
							</Box>
							{studyData[0]?.subTopics?.map((item, index) => (
								<Box
									key={index}
									sx={{
										borderBottom:
											item === selectedTopic &&
											"4px solid #2e95ff",
										borderRadius: "2px",
										margin: "3px",
										textAlign: "center",
										":hover": {
											cursor: "pointer"
										}
									}}
									onClick={() => handleSelectTopic(item)}
								>
									<Typography
										fontWeight="bold"
										sx={{
											fontSize: "15px",
											color: "#4858a6"
										}}
									>
										{item}
									</Typography>
								</Box>
							))}
						</Box>

						<Box sx={{ marginTop: "20px" }}>
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
										sx={{
											fontSize: "18px",
											color: "#4858a6"
										}}
									>
										{studyData[0]?.topic}
									</Typography>
								</Box>
							</Box>
							<Divider />
							{subTopicData ? (
								<FilterData searchResult={subTopicData} />
							) : (
								<Box sx={{ display: "flex" }}>
									<Box sx={{ width: "70%" }}>
										{material?.map((item) => (
											<Paper
												sx={{
													padding: "8px",
													width: "45%",
													display: "inline-block",
													margin: "5px",
													":hover": {
														cursor: "pointer"
													}
												}}
											>
												<Box>
													<CardMedia
														src={
															window.location
																.origin +
															item.videoUrl
														}
														component="video"
														controls
														style={{
															width: "100%",
															height: "200px"
														}}
													/>
												</Box>
												<Box>
													<Typography
														fontWeight="bold"
														sx={{
															fontSize: "15px",
															color: "#6e6e6e"
														}}
													>
														{item.videoHeader}
													</Typography>
												</Box>
												<Box>
													<Typography
														fontWeight="bold"
														sx={{
															fontSize: "13px",
															color: "#6e6e6e"
														}}
													>
														112k Views
													</Typography>
												</Box>
											</Paper>
										))}
									</Box>
									<Box
										sx={{
											width: "35%",
											height: "70vh",
											padding: "10px",
											borderLeft: "1px solid #e6e6e6"
										}}
									>
										<Box>
											<Box
												sx={{
													display: "flex",
													justifyContent: "center"
												}}
											>
												<Typography
													fontSize="18px"
													color="info.dark"
													fontWeight="bold"
												>
													Summary
												</Typography>
											</Box>
											<Typography
												variant="textSizeParagraph"
												dangerouslySetInnerHTML={{
													__html: `${studyData[0]?.summary} `
												}}
											/>

											{/* <Typography>
												{studyData[0]?.summary}
											</Typography> */}
										</Box>
										<Box>
											<Divider />
											<Box
												sx={{
													display: "flex",
													justifyContent: "center"
												}}
											>
												<Typography
													fontSize="18px"
													color="info.dark"
													fontWeight="bold"
												>
													Topics
												</Typography>
											</Box>

											<Box sx={{ margin: "2px" }}>
												{studyData[0]?.topics
													.slice(0, 8)
													.map((item) => (
														<Chip
															sx={{
																fontSize:
																	"12px",
																margin: "4px"
															}}
															label={item}
															color="primary"
														/>
													))}
											</Box>
											<Divider />
										</Box>
										<Box>
											<Box
												sx={{
													display: "flex",
													justifyContent: "center"
												}}
											>
												<Typography
													fontSize="18px"
													color="info.dark"
													fontWeight="bold"
												>
													Features
												</Typography>
											</Box>

											<Box sx={{ margin: "2px" }}>
												{studyData[0]?.features
													.slice(0, 6)
													.map((item) => (
														<Chip
															sx={{
																fontSize:
																	"12px",
																margin: "4px"
															}}
															label={item}
															color="primary"
														/>
													))}
											</Box>
											<Divider />
										</Box>
									</Box>
								</Box>
							)}
						</Box>
					</>
				)}
			</Box>
		</Box>
	);
};
export default TopicMaterial;
