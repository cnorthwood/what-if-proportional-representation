import React from "react";
import ReactDOM from "react-dom";

import App from "./App";
import data from "./data.json";

import "./index.scss"

ReactDOM.render(<App {...data} />, document.getElementById("root"));

