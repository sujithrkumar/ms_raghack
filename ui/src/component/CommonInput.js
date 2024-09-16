import { TextField, styled } from "@mui/material";
export const CustomLoginInputField = styled(TextField)(({ theme }) => ({
	"& .MuiInputBase-input": {
		borderBottom: ".2px solid ",
		borderColor: theme.palette.secondary.placeholderColor,
		color: theme.palette.secondary.placeholderColor,
		fontSize: "18px",
		fontFamily: "inherit"
	},
	"& .MuiInput-input": {
		"&:-webkit-autofill": {
			transitionDelay: "9999s",
			WebkitBoxShadow: "0 0 0 1000px #365a77 inset"
		},
		"&::placeholder": {
			fontSize: "21px",
			[theme.breakpoints.down("large")]: {
				fontSize: "18px"
			},
			[theme.breakpoints.down("laptop")]: {
				fontSize: "18px"
			},
			[theme.breakpoints.down("tablet")]: {
				fontSize: "18px"
			}
		}
	},
	"& .MuiInput-underline": {
		":before": {
			display: "none"
		},
		":after": {
			display: "none"
		}
	},
	width: "80%"
}));

export const CustomLoginInputoutlinedField = styled(TextField)(({ theme }) => ({
	"& .MuiInputBase-input": {
		border: ".2px solid ",
		borderColor: theme.palette.secondary.placeholderColor,
		color: theme.palette.secondary.placeholderColor,
		fontSize: "18px"
	},
	"& .MuiInput-input": {
		"&:-webkit-autofill": {
			transitionDelay: "9999s",
			WebkitBoxShadow: "0 0 0 1000px #365a77 inset"
		},
		"&::placeholder": {
			fontSize: "21px",
			[theme.breakpoints.down("large")]: {
				fontSize: "18px"
			},
			[theme.breakpoints.down("laptop")]: {
				fontSize: "18px"
			},
			[theme.breakpoints.down("tablet")]: {
				fontSize: "18px"
			}
		}
	},
	"& .MuiInput-underline": {
		":before": {
			display: "none"
		},
		":after": {
			display: "none"
		}
	},

	width: "80%"
}));
