import { GeoJsonObject } from "geojson";
import React, { ChangeEvent, Component, createRef, RefObject } from "react";
import { GeoJSON, Map, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

import Constituency from "./components/Constituency";
import Seats from "./components/Seats";

export interface VisualisationProps {
  parliament: Record<string, number>;
  constituencies: Record<
    string,
    {
      electorate: string;
      seats: number;
      formedFrom: string[];
      seatAllocations: Record<string, number>;
      votes: Record<string, number>;
    }
  >;
  topup?: Record<string, number>;
}

interface VisualisationState {
  selectedConstituency: string | null;
  geometry: GeoJsonObject | null;
  geometries: Record<string, GeoJsonObject>;
  geometryLoading: boolean;
}

export default class Visualisation extends Component<VisualisationProps, VisualisationState> {
  private mapRef: RefObject<Map>;

  constructor(props: VisualisationProps) {
    super(props);
    this.state = {
      selectedConstituency: new URLSearchParams(window.location.search).get("constituency"),
      geometry: null,
      geometries: {},
      geometryLoading: false,
    };
    this.onChangeConstituency = this.onChangeConstituency.bind(this);
    this.mapRef = createRef();
  }

  public componentDidMount() {
    this.loadGeometry();
  }

  public componentDidUpdate(prevProps: Readonly<VisualisationProps>, prevState: Readonly<VisualisationState>) {
    if (prevState.selectedConstituency !== this.state.selectedConstituency) {
      this.loadGeometry();
    }
  }

  public render() {
    return (
      <>
        <h2 className="subtitle">Parliament (300 needed for majority)</h2>
        <Seats seats={this.props.parliament} topup={this.props.topup} />
        <h2 className="subtitle">Constituencies</h2>
        <div className="columns">
          <div className={`column ${this.state.geometryLoading ? "is-loading" : ""}`}>
            <Map center={[54.093409, -2.89479]} zoom={5} ref={this.mapRef}>
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
              />
              {this.state.geometry ? <GeoJSON data={this.state.geometry} /> : null}
            </Map>
          </div>
          <div className="column">
            <div className="field">
              <label className="label" htmlFor="select-constituency">
                Select a constituency:
              </label>
              <div className="control">
                <div className="select">
                  <select
                    name="select-constituency"
                    id="select-constituency"
                    value={this.state.selectedConstituency || ""}
                    onChange={this.onChangeConstituency}
                  >
                    {this.state.selectedConstituency === null ? <option /> : null}
                    {this.getExistingConstituencies().map(constituency => (
                      <option key={constituency}>{constituency}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            {this.state.selectedConstituency === null ? (
              <div className="message is-info">
                <p className="message-body">
                  Please select your current constituency from the list above, to see what the
                  results would look like under this new system.
                </p>
              </div>
            ) : (
              <Constituency {...this.currentConstituency()!} />
            )}
          </div>
        </div>
      </>
    );
  }

  private onChangeConstituency(ev: ChangeEvent<HTMLSelectElement>) {
    this.setState({ selectedConstituency: ev.currentTarget.value });
    window.history.replaceState("", "", `?constituency=${ev.currentTarget.value}`);
  }

  private currentConstituency() {
    return this.getConstituencyFromOldConstituency(this.state.selectedConstituency);
  }

  private getConstituencyFromOldConstituency(existingConstituency: string | null) {
    if (!existingConstituency) {
      return null;
    }
    for (let constituencyName in this.props.constituencies) {
      const constituency = this.props.constituencies[constituencyName];
      if (constituency.formedFrom.includes(existingConstituency)) {
        return { name: constituencyName, ...constituency };
      }
    }
    return null;
  }

  private getExistingConstituencies() {
    const existingConstituencies: string[] = [];
    Object.values(this.props.constituencies).forEach(constituency => {
      existingConstituencies.push(...constituency.formedFrom);
    });
    return existingConstituencies.sort();
  }

  private async loadGeometry() {
    const currentConstituency = this.currentConstituency();
    if (!currentConstituency) {
      return;
    }
    this.setState({ geometry: null, geometryLoading: true });
    const constituencyName = currentConstituency.name;
    if (this.state.geometries[constituencyName]) {
      this.setState({ geometry: this.state.geometries[constituencyName], geometryLoading: false });
      return;
    }

    const response = await fetch(`geometries/${constituencyName}.geojson`);
    const geometry = (await response.json()) as GeoJsonObject;
    const maybeChangedConstituency = this.currentConstituency();
    this.setState({ geometries: { ...this.state.geometries, [constituencyName]: geometry } });
    if (maybeChangedConstituency && maybeChangedConstituency.name === constituencyName) {
      this.setState({ geometry, geometryLoading: false });
    }
  }
}
