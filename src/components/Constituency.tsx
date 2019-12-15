import React, { FunctionComponent } from "react";
import Seats from "./Seats";

interface ConstituencyProps {
  name: string;
  electorate: string;
  seats: number;
  formedFrom: string[];
  seatAllocations: Record<string, number>;
  votes: Record<string, number>;
}

const Constituency: FunctionComponent<ConstituencyProps> = ({
  name,
  electorate,
  seats,
  formedFrom,
  votes,
  seatAllocations,
}) => (
  <div className="box">
    <h3 className="title">New Name: <i>{name}</i></h3>
    <Seats seats={seatAllocations} votes={votes} />
    <div className="content">
      <p>This seat has {electorate} voters in it, elects {seats} MPs, and was formed from:</p>
      <ul>
        {formedFrom.sort().map(seatName => (
          <li key={seatName}>{seatName}</li>
        ))}
      </ul>
    </div>
  </div>
);
export default Constituency;
