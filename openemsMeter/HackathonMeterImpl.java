package de.voltfang.edge.meter.hackathon;


import io.openems.edge.meter.api.MeterType;
import org.osgi.service.cm.ConfigurationAdmin;
import org.osgi.service.component.ComponentContext;
import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.ConfigurationPolicy;
import org.osgi.service.component.annotations.Deactivate;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.osgi.service.component.annotations.ReferencePolicy;
import org.osgi.service.component.annotations.ReferencePolicyOption;
import org.osgi.service.metatype.annotations.Designate;

import io.openems.common.exceptions.OpenemsException;
import io.openems.edge.bridge.modbus.api.AbstractOpenemsModbusComponent;
import io.openems.edge.bridge.modbus.api.BridgeModbus;
import io.openems.edge.bridge.modbus.api.ModbusComponent;
import io.openems.edge.bridge.modbus.api.ModbusProtocol;
import io.openems.edge.bridge.modbus.api.element.DummyRegisterElement;
import io.openems.edge.bridge.modbus.api.element.FloatDoublewordElement;
import io.openems.edge.bridge.modbus.api.element.SignedDoublewordElement;
import io.openems.edge.bridge.modbus.api.element.WordOrder;
import io.openems.edge.bridge.modbus.api.task.FC4ReadInputRegistersTask;
import io.openems.edge.common.component.OpenemsComponent;
import io.openems.edge.common.taskmanager.Priority;
import io.openems.edge.meter.api.ElectricityMeter;

@Designate(ocd = Config.class, factory = true)
@Component(//
		name = "Meter.Voltfang.Hackathon", //
		immediate = true, //
		configurationPolicy = ConfigurationPolicy.REQUIRE //
)
public class HackathonMeterImpl extends AbstractOpenemsModbusComponent
		implements HackathonMeter, ElectricityMeter, ModbusComponent, OpenemsComponent {

	@Reference
	private ConfigurationAdmin cm;

	@Override
	@Reference(policy = ReferencePolicy.STATIC, policyOption = ReferencePolicyOption.GREEDY, cardinality = ReferenceCardinality.MANDATORY)
	protected void setModbus(BridgeModbus modbus) {
		super.setModbus(modbus);
	}

	private Config config;

	public HackathonMeterImpl() {
		super(//
				OpenemsComponent.ChannelId.values(), //
				ModbusComponent.ChannelId.values(), //
				ElectricityMeter.ChannelId.values(), //
				HackathonMeter.ChannelId.values() //
		);

		// Automatically calculate sum values from L1/L2/L3
		ElectricityMeter.calculateSumCurrentFromPhases(this);
		ElectricityMeter.calculateAverageVoltageFromPhases(this);
	}

	@Activate
	private void activate(ComponentContext context, Config config) throws OpenemsException {
		this.config = config;

		if (super.activate(context, config.id(), config.alias(), config.enabled(), config.modbusUnitId(), this.cm,
				"Modbus", config.modbus_id())) {
			return;
		}
	}

	@Override
	@Deactivate
	protected void deactivate() {
		super.deactivate();
	}

	@Override
	public MeterType getMeterType() {
		return this.config.type();
	}

	@Override
	protected ModbusProtocol defineModbusProtocol() {
		return new ModbusProtocol(this,
			new FC4ReadInputRegistersTask(2001, Priority.HIGH,
				m(ElectricityMeter.ChannelId.VOLTAGE_L1, new FloatDoublewordElement(2001)),
				m(ElectricityMeter.ChannelId.VOLTAGE_L2, new FloatDoublewordElement(2003)),
				m(ElectricityMeter.ChannelId.VOLTAGE_L3, new FloatDoublewordElement(2005)),
				new DummyRegisterElement(2007, 2012)),
			new FC4ReadInputRegistersTask(2013, Priority.HIGH,
				m(ElectricityMeter.ChannelId.CURRENT_L1, new FloatDoublewordElement(2013)),
				m(ElectricityMeter.ChannelId.ACTIVE_POWER_L1, new FloatDoublewordElement(2015)),
				m(HackathonMeter.ChannelId.APPARENT_POWER_L1, new FloatDoublewordElement(2017)),
				m(ElectricityMeter.ChannelId.REACTIVE_POWER_L1, new FloatDoublewordElement(2019)),
				m(ElectricityMeter.ChannelId.CURRENT_L2, new FloatDoublewordElement(2021)),
				m(ElectricityMeter.ChannelId.ACTIVE_POWER_L2, new FloatDoublewordElement(2023)),
				m(HackathonMeter.ChannelId.APPARENT_POWER_L2, new FloatDoublewordElement(2025)),
				m(ElectricityMeter.ChannelId.REACTIVE_POWER_L2, new FloatDoublewordElement(2027)),
				m(ElectricityMeter.ChannelId.CURRENT_L3, new FloatDoublewordElement(2029)),
				m(ElectricityMeter.ChannelId.ACTIVE_POWER_L3, new FloatDoublewordElement(2031)),
				m(HackathonMeter.ChannelId.APPARENT_POWER_L3, new FloatDoublewordElement(2033)),
				m(ElectricityMeter.ChannelId.REACTIVE_POWER_L3, new FloatDoublewordElement(2035))),
			new FC4ReadInputRegistersTask(2037, Priority.LOW,
				new DummyRegisterElement(2037, 2040),
				m(ElectricityMeter.ChannelId.ACTIVE_POWER, new FloatDoublewordElement(2041)),
				m(HackathonMeter.ChannelId.APPARENT_POWER, new FloatDoublewordElement(2043)),
				m(ElectricityMeter.ChannelId.REACTIVE_POWER, new FloatDoublewordElement(2045)),
				new DummyRegisterElement(2047, 2051),
				m(ElectricityMeter.ChannelId.FREQUENCY, new FloatDoublewordElement(2052)),
				new DummyRegisterElement(2054, 2080))
		);
	}

	@Override
	public String debugLog() {
		return "L :" + this.getActivePower().asString()+ "L1: " + this.getActivePowerL1().asString();
	}
}