import React, { Component } from "react";

import Visualisation, { VisualisationProps } from "./Visualisation";
import data from "./data.json";

interface AppProps {}
interface AppState {
  data?: VisualisationProps;
}

export default class App extends Component<AppProps, AppState> {
  constructor(props: AppProps) {
    super(props);
    this.state = {};
  }

  public render() {
    return (
      <>
        <div className="columns content">
          <div className="column">
            <h2 className="title">Multi-member Constituencies</h2>
            <p>
              Instead of having 1 MP to represent an area, we can imagine having many. In this
              experiment, I've combined our existing constituency boundaries into new
              constituencies, which overall elect 600 MPs to Parliament (the number proposed under
              the most recent electoral reform), but each constituency elects on average 8 MPs. The{" "}
              <a href="https://en.wikipedia.org/wiki/D%27Hondt_method">D'Hondt method</a> is used to
              determine the allocation of parties to seats.
            </p>
            <p>
              <button
                className="button is-primary"
                onClick={() => {
                  this.setState({ data: data.multimember });
                }}
              >
                Run this experiment
              </button>
            </p>
          </div>
          <div className="column">
            <h2 className="title">Top-up votes</h2>
            <p>
              This experiment is like the other one, with larger, multi-member seats, but only 300
              MPs are sent to parliament. The other 300 MPs in parliament are determined by the national
              vote (so, pure PR using D'Hondt).
            </p>
            <p>
              <button
                className="button is-primary"
                onClick={() => {
                  this.setState({ data: data.withTopup });
                }}
              >
                Run this experiment
              </button>
            </p>
          </div>
        </div>
        {this.state.data ? <Visualisation {...this.state.data} /> : null}
      </>
    );
  }
}
