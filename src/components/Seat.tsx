import React, { FunctionComponent } from "react";

const cssClass = (partyName: string) => partyName.replace(" ", "-");

const Seat: FunctionComponent<{ party: string }> = ({ party }) => (
  <span className={`parliament__seat parliament__seat--${cssClass(party)}`} title={party} />
);
export default Seat;
