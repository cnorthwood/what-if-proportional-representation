import React, { FunctionComponent } from "react";
import times from "lodash/times";
import Seat from "./Seat";

const Seats: FunctionComponent<{
  seats: Record<string, number>;
  votes?: Record<string, number>;
}> = ({ seats, votes }) => (
  <>
    {" "}
    <div className="columns">
      {Object.keys(seats)
        .filter(partyName => seats[partyName] > 0)
        .map(partyName => (
          <div key={partyName} className="column has-text-centered">
            <span className="parliament__party-name">{partyName}</span>
            <br />
            <span className="is-size-1">{seats[partyName]}</span>
            <p>{votes ? <>{votes[partyName].toLocaleString()} votes</> : null}</p>
          </div>
        ))}
      {votes ? (
        <div className="column">
          <span className="parliament__party-name">Did Not Win</span>
          <ul>
            {Object.keys(seats)
              .filter(partyName => seats[partyName] === 0)
              .sort((a, b) => votes[b] - votes[a])
              .map(partyName => (
                <li key={partyName}>
                  <i>{partyName}</i>: {votes[partyName].toLocaleString()} votes
                </li>
              ))}
          </ul>
        </div>
      ) : null}
    </div>
    {votes ? null : (
      <div className="parliament">
        {Object.keys(seats).map(partyName =>
          times(seats[partyName]).map(i => <Seat key={`${partyName}-${i}`} party={partyName} />),
        )}
      </div>
    )}
  </>
);
export default Seats;
