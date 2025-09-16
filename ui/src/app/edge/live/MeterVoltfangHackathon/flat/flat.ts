// @ts-strict-ignore
import { Component } from "@angular/core";
import { AbstractFlatWidget } from "src/app/shared/components/flat/abstract-flat-widget";


@Component({
  selector: "Meter_Voltfang_Hackathon",
  templateUrl: "./flat.html",
  standalone: false,
})
export class FlatComponent extends AbstractFlatWidget {

  public readonly FREQUENCY_IN_HERTZ = (frequency: number): string => frequency + " Hz";

}
