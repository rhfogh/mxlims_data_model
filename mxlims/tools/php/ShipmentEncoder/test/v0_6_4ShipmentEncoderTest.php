<?php

namespace mxlims\tools\php\ShipmentEncoder\test;

use PHPUnit\Framework\TestCase;

class v0_6_4ShipmentEncoderTest extends TestCase {

	public function setUp(): void {
		if(!$this->version ||!$this->encoder){
			$parts = explode('\\', get_called_class());
			$className = end($parts);
			$className = str_replace('Test', '', $className);
			if (!preg_match('/\d+_\d+_\d+/', $className, $matches)) {
				die('Cannot determine version from class name');
			}
			$version = str_replace('_', '.', $matches[0]);
			$this->version = $version;
			include_once '../src/' . $className . '.php';
			$fullClassName = 'mxlims\tools\php\ShipmentEncoder\src\\' . $className;
			$this->encoder = new $fullClassName();
		}
	}

	public function tearDown(): void {
		unset($this->encoder);
		@unlink(__DIR__.'/test.json');
	}

	public function testGetVersion() {
		$version = $this->encoder->getVersion();
		$this->assertEquals($this->version, $version);
	}

	public function testGet() {
		$this->encoder->createShipment('mx4025', 1);
		$shipment = $this->encoder->get('Shipment', 1);
		self::assertNotEmpty($shipment);
		self::assertEquals('Shipment', $shipment['mxlimsType']);
		self::assertEquals(1, $shipment['index']);
	}

	public function testGetByJsonPath() {
		$this->encoder->createShipment('mx4025', 1);
		$shipment=$this->encoder->getByJsonPath('#/Shipment/Shipment1');
		self::assertNotEmpty($shipment);
		self::assertEquals('Shipment', $shipment['mxlimsType']);
		self::assertEquals(1, $shipment['index']);
	}

	public function testGetByJsonPathWithRef() {
		$this->encoder->createShipment('mx4025', 1);
		$shipment=$this->encoder->getByJsonPath(['$ref'=>'#/Shipment/Shipment1']);
		self::assertNotEmpty($shipment);
		self::assertEquals('Shipment', $shipment['mxlimsType']);
		self::assertEquals(1, $shipment['index']);
	}

	public function testGetNonExistent() {
		$shipment = $this->encoder->get('Shipment', 1);
		self::assertNull($shipment);
	}

	public function testCreateShipment() {
		$shipment = $this->encoder->createShipment('mx4025', 1);
		$this->assertEquals('mx4025', $shipment['proposalCode']);
		$this->assertEquals(1, $shipment['sessionNumber']);
		$this->assertEquals('Shipment', $shipment['mxlimsType']);
		$this->assertEquals($this->version, $shipment['version']);
		$this->assertNotEmpty($shipment['uuid']);
		$this->assertEquals(1, $shipment['index']);
	}

	public function testCreateShipmentNoSessionNumber() {
		$shipment = $this->encoder->createShipment('mx4025');
		$this->assertEquals('mx4025', $shipment['proposalCode']);
		$this->assertArrayNotHasKey('sessionNumber', $shipment);
		$this->assertEquals('Shipment', $shipment['mxlimsType']);
		$this->assertEquals($this->version, $shipment['version']);
		$this->assertNotEmpty($shipment['uuid']);
	}

	public function testCreateShipmentTwice() {
		$this->expectExceptionMessageMatches('~Shipment already added to message~');
		$this->encoder->createShipment('mx4025', 1);
		$this->encoder->createShipment('mx4025', 1);
	}

	public function testSetLabContactOutbound() {
		$labContact = $this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->assertEquals('Bob', $labContact['name']);
		$this->assertEquals('bob@bob.com', $labContact['emailAddress']);
		$this->assertArrayNotHasKey('phoneNumber', $labContact);
	}

	public function testSetLabContactReturn() {
		$labContact = $this->encoder->setLabContactReturn('Bob', 'bob@bob.com');
		$this->assertEquals('Bob', $labContact['name']);
		$this->assertEquals('bob@bob.com', $labContact['emailAddress']);
		$this->assertArrayNotHasKey('phoneNumber', $labContact);
	}

	public function testSetLabContactReturnBothContactDetails() {
		$labContact = $this->encoder->setLabContactReturn('Bob', 'bob@bob.com', '1-800-BOB-1234');
		$this->assertEquals('Bob', $labContact['name']);
		$this->assertEquals('bob@bob.com', $labContact['emailAddress']);
		$this->assertEquals('1-800-BOB-1234', $labContact['phoneNumber']);
	}

	public function testSetLabContactReturnNoContactDetails() {
		$this->expectExceptionMessageMatches('~Email or phone number~');
		$this->encoder->setLabContactReturn('Bob');
	}

	public function testAddDewarToShipment() {
		$this->encoder->createShipment('mx4025', 1);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$this->assertEquals('DLS-MX-1234', $dewar['barcode']);
		$this->assertEquals('Dewar', $dewar['mxlimsType']);
		$this->assertArrayHasKey('uuid', $dewar);
		$this->assertEquals(1, $dewar['index']);
	}

	public function testAddDewarToShipmentNoShipment() {
		$this->expectExceptionMessageMatches('~Call createShipment~');
		$this->encoder->addDewarToShipment('DLS-MX-1234');
	}

	public function testAddDewarToShipmentPlateExists() {
		$this->expectExceptionMessageMatches('~Shipment contains Plates~');
		$this->encoder->createShipment('mx4025', 1);
		$this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$this->encoder->addDewarToShipment('DLS-MX-1234');

	}

	public function testAddPuckToDewar() {
		$this->encoder->createShipment('mx4025', 1);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->assertEquals('OUL-999', $puck['barcode']);
		$this->assertEquals('Puck', $puck['mxlimsType']);
		$this->assertArrayHasKey('uuid', $puck);
		$this->assertEquals(1, $puck['index']);
	}

	public function testAddPuckToDewarNoDewar() {
		$this->expectExceptionMessageMatches('~No dewar with index~');
		$this->encoder->createShipment('mx4025', 1);
		$this->encoder->addPuckToDewar(1, 'OUL-999', 16);
	}

	public function testAddMacromoleculeToShipment() {
		$this->encoder->createShipment('mx4025', 1);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$this->assertEquals(1, $macromolecule['index']);
		$this->assertEquals('TEST', $macromolecule['acronym']);
		$this->assertEquals('Macromolecule', $macromolecule['mxlimsType']);
		$this->assertNotEmpty($macromolecule['uuid']);
	}

	public function testAddMacromoleculeToShipmentNoAcronym() {
		$this->encoder->createShipment('mx4025', 1);
		$this->expectExceptionMessageMatches('~cannot be empty~');
		$this->encoder->addMacromoleculeToShipment('');
	}

	public function testAddSinglePinSampleToPuck() {
		$this->encoder->createShipment('mx4025', 1);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$pinAndSample = $this->encoder->addSinglePinSampleToPuck($puck['index'], 1, $macromolecule['index'], 'TEST_9098A01d1c1', 'HA00AA5432');
		$this->assertArrayHasKey('Pin', $pinAndSample);
		$this->assertArrayHasKey('MacromoleculeSample', $pinAndSample);
		$pin = $pinAndSample['Pin'];
		$this->assertEquals('HA00AA5432', $pin['barcode']);
		$this->assertEquals('#/Puck/Puck' . $puck['index'], $pin['containerRef']['$ref']);
		$this->assertEquals('#/MacromoleculeSample/MacromoleculeSample' . $pin['index'], $pin['sampleRef']['$ref']);
		$this->assertNotEmpty($pin['uuid']);
		$sample = $pinAndSample['MacromoleculeSample'];
		$this->assertEquals('TEST_9098A01d1c1', $sample['name']);
		$this->assertNotEmpty($sample['uuid']);
	}

	public function testAddSinglePinSampleToPuckMultiPinExists() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$this->encoder->addMultiPositionPinToPuck($puck['index'], 4, 8, 'PIN1');
		$this->expectExceptionMessageMatches('~Cannot mix multi-position pins~');
		$this->encoder->addSinglePinSampleToPuck(2, 1, $macromolecule['index'], 'TEST_9098A01d1c1', 'HA00AA5432');
	}

	public function testAddSinglePinSampleToPuckBadPuckIndex() {
		$this->encoder->createShipment('mx4025', 11);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->expectExceptionMessageMatches('~No puck with index~');
		$this->encoder->addSinglePinSampleToPuck(2, 1, $macromolecule['index'], 'TEST_9098A01d1c1', 'HA00AA5432');
	}

	public function testAddSinglePinSampleToPuckBadMacromoleculeIndex() {
		$this->encoder->createShipment('mx4025', 1);
		$this->encoder->addMacromoleculeToShipment('TEST');
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->expectExceptionMessageMatches('~No macromolecule with index~');
		$this->encoder->addSinglePinSampleToPuck($puck['index'], 1, 2, 'TEST_9098A01d1c1', 'HA00AA5432');
	}

	public function testAddSinglePinSampleToPuckPositionOutOfRange() {
		$this->encoder->createShipment('mx4025', 1);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->expectExceptionMessageMatches('~Puck position must be between~');
		$this->encoder->addSinglePinSampleToPuck($puck['index'], 17, $macromolecule['index'], 'TEST_9098A01d1c1', 'HA00AA5432');
	}

	public function testAddSinglePinSampleToPuckPositionFull() {
		$this->encoder->createShipment('mx4025', 1);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->expectExceptionMessageMatches('~already filled~');
		$this->encoder->addSinglePinSampleToPuck($puck['index'], 4, $macromolecule['index'], 'TEST_9098A01d1c1', 'HA00AA5432');
		$this->encoder->addSinglePinSampleToPuck($puck['index'], 4, $macromolecule['index'], 'TEST_9098A01d1c2', 'HA00AA5434');
	}

	public function testAddSinglePinSampleToPuckDuplicateBarcode() {
		$this->encoder->createShipment('mx4025', 2);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->encoder->addSinglePinSampleToPuck($puck['index'], 4, $macromolecule['index'], 'TEST_9098A01d1c1', 'HA00AA5432');
		$this->expectExceptionMessageMatches('~Shipment already contains a pin with barcode~');
		$this->encoder->addSinglePinSampleToPuck($puck['index'], 5, $macromolecule['index'], 'TEST_9098A01d1c2', 'HA00AA5432');
	}

	public function testAddMultiPositionPinToPuck() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$pin = $this->encoder->addMultiPositionPinToPuck($puck['index'], 4, 8, 'MULTIPIN1');
		$this->assertEquals('MULTIPIN1', $pin['barcode']);
		$this->assertEquals('#/Puck/Puck' . $puck['index'], $pin['containerRef']['$ref']);
		$this->assertEquals(4, $pin['positionInPuck']);
		$this->assertEquals(8, $pin['numberPositions']);
		$this->assertEquals(1, $pin['index']);
	}

	public function testAddMultiPositionPinToPuckSinglePositionPinExists() {
		$this->encoder->createShipment('mx4025', 4);
		$this->encoder->addMacromoleculeToShipment('TEST');
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->encoder->addSinglePinSampleToPuck($puck['index'], 1, 1, 'TEST_9098A01d1c1', 'HA00AA5432');
		$this->expectExceptionMessageMatches('~contains single-position pin~');
		$this->encoder->addMultiPositionPinToPuck($puck['index'], 4, 8, 'MULTIPIN1');
	}

	public function testAddMultiPositionPinNoPuck() {
		$this->expectExceptionMessageMatches('~No puck with index~');
		$this->encoder->addMultiPositionPinToPuck(1, 4, 8, 'MULTIPIN1');
	}

	public function testAddMultiPositionPinBadPositionCount() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->expectExceptionMessageMatches('~positions must be a positive integer~');
		$this->encoder->addMultiPositionPinToPuck($puck['index'], 4, 0, 'MULTIPIN1');
	}

	public function testAddMultiPositionPinBadPuckPosition() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->expectExceptionMessageMatches('~Position in puck must be between~');
		$this->encoder->addMultiPositionPinToPuck($puck['index'], 17, 8, 'MULTIPIN1');
	}

	public function testAddMultiPositionPinPuckPositionFull() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->encoder->addMultiPositionPinToPuck($puck['index'], 10, 8, 'MULTIPIN1');
		$this->expectExceptionMessageMatches('~already filled~');
		$this->encoder->addMultiPositionPinToPuck($puck['index'], 10, 8, 'MULTIPIN1');
	}

	public function testAddSinglePinSampleToPuckDuplicateSampleName() {
		$this->encoder->createShipment('mx4025', 3);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->encoder->addSinglePinSampleToPuck($puck['index'], 4, $macromolecule['index'], 'TEST_9098A01d1c1', 'HA00AA5432');
		$this->expectExceptionMessageMatches('~Shipment already contains a sample with name~');
		$this->encoder->addSinglePinSampleToPuck($puck['index'], 5, $macromolecule['index'], 'TEST_9098A01d1c1', 'HA00AA5434');
	}

	public function testAddSinglePositionPinToPuck() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$pin = $this->encoder->addSinglePositionPinToPuck($puck['index'], 4, 'MULTIPIN1');
		$this->assertEquals('MULTIPIN1', $pin['barcode']);
		$this->assertEquals('#/Puck/Puck' . $puck['index'], $pin['containerRef']['$ref']);
		$this->assertEquals(4, $pin['positionInPuck']);
		$this->assertEquals(1, $pin['index']);
	}

	public function testAddSinglePositionPinToPuckMultiPositionPinExists() {
		$this->encoder->createShipment('mx4025', 4);
		$this->encoder->addMacromoleculeToShipment('TEST');
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->encoder->addMultiPositionPinToPuck($puck['index'], 4, 8, 'MULTIPIN1');
		$this->expectExceptionMessageMatches('~contains multi-position pin~');
		$this->encoder->addSinglePositionPinToPuck($puck['index'], 1, 'HA00AA5432');
	}

	public function testAddSinglePositionPinNoPuck() {
		$this->expectExceptionMessageMatches('~No puck with index~');
		$this->encoder->addSinglePositionPinToPuck(1, 4, 'MULTIPIN1');
	}

	public function testAddSinglePositionPinBadPuckPosition() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->expectExceptionMessageMatches('~Position in puck must be between~');
		$this->encoder->addSinglePositionPinToPuck($puck['index'], 17, 'PIN1');
	}

	public function testAddSinglePositionPinPuckPositionFull() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->encoder->addSinglePositionPinToPuck($puck['index'], 10, 'PIN1');
		$this->expectExceptionMessageMatches('~already filled~');
		$this->encoder->addSinglePositionPinToPuck($puck['index'], 10, 'MULTIPIN1');
	}

	public function testAddSampleToMultiPositionPin() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$pin = $this->encoder->addMultiPositionPinToPuck($puck['index'], 10, 8, 'MULTIPIN1');
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$ret = $this->encoder->addSampleToMultiPositionPin($pin['index'], 1, $macromolecule['index'], 'TEST_9098A01d1c1');
		$this->assertArrayHasKey('MacromoleculeSample', $ret);
		$this->assertEquals('TEST_9098A01d1c1', $ret['MacromoleculeSample']['name']);
		$this->assertEquals('#/Macromolecule/Macromolecule' . $macromolecule['index'], $ret['MacromoleculeSample']['macromoleculeRef']['$ref']);
		$this->assertArrayHasKey('PinPosition', $ret);
		$this->assertEquals(1, $ret['PinPosition']['positionInPin']);
		$this->assertEquals('#/MacromoleculeSample/MacromoleculeSample' . $ret['MacromoleculeSample']['index'], $ret['PinPosition']['sampleRef']['$ref']);
		$this->assertEquals('#/MultiPin/MultiPin' . $pin['index'], $ret['PinPosition']['containerRef']['$ref']);
	}

	public function testAddSampleToMultiPositionPinNoPin() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$this->expectExceptionMessageMatches('~No pin~');
		$this->encoder->addSampleToMultiPositionPin(1, 1, $macromolecule['index'], 'TEST_9098A01d1c1');
	}

	public function testAddSampleToMultiPositionPinNoMacromolecule() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$pin = $this->encoder->addMultiPositionPinToPuck($puck['index'], 10, 8, 'MULTIPIN1');
		$this->expectExceptionMessageMatches('~No macromolecule~');
		$this->encoder->addSampleToMultiPositionPin($pin['index'], 1, 1, 'TEST_9098A01d1c1');
	}

	public function testAddSampleToMultiPositionPinPositionFull() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$pin = $this->encoder->addMultiPositionPinToPuck($puck['index'], 10, 8, 'MULTIPIN1');
		$this->encoder->addSampleToMultiPositionPin($pin['index'], 1, $macromolecule['index'], 'TEST_9098A01d1c1');
		$this->expectExceptionMessageMatches('~already filled~');
		$this->encoder->addSampleToMultiPositionPin($pin['index'], 1, $macromolecule['index'], 'TEST_9098A01d1c2');
	}

	public function testAddSampleToMultiPositionPinDuplicateSampleName() {
		$this->encoder->createShipment('mx4025', 4);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$pin = $this->encoder->addMultiPositionPinToPuck($puck['index'], 10, 8, 'MULTIPIN1');
		$this->encoder->addSampleToMultiPositionPin($pin['index'], 1, $macromolecule['index'], 'TEST_9098A01d1c1');
		$this->expectExceptionMessageMatches('~name already exists~');
		$this->encoder->addSampleToMultiPositionPin($pin['index'], 2, $macromolecule['index'], 'TEST_9098A01d1c1');
	}

	public function testAddPlateToShipment() {
		$this->encoder->createShipment('mx4025', 1);
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$this->assertEquals('BARCODE1234', $plate['barcode']);
		$this->assertEquals('Plate', $plate['mxlimsType']);
		$this->assertArrayHasKey('uuid', $plate);
		$this->assertEquals(1, $plate['index']);
		$this->assertArrayHasKey('plateType', $plate);
		$this->assertEquals(8, $plate['plateType']['numberRows']);
		$this->assertEquals(12, $plate['plateType']['numberColumns']);
		$this->assertEquals(3, $plate['plateType']['numberSubPositions']);
		$this->assertEquals('123,RRR', $plate['plateType']['dropMapping']);
	}

	public function testAddPlateToShipmentNoShipment() {
		$this->expectExceptionMessageMatches('~Call createShipment~');
		$this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
	}

	public function testAddPlateToShipmentDewarExists() {
		$this->expectExceptionMessageMatches('~Shipment contains Dewars~');
		$this->encoder->createShipment('mx4025', 1);
		$this->encoder->addDewarToShipment('DLS-MX-1234');
		$this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
	}

	public function testAddPlateToShipmentTwice() {
		$this->expectExceptionMessageMatches('~already in shipment~');
		$this->encoder->createShipment('mx4025', 1);
		$this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
	}

	public function testAddWellToPlate() {
		$this->encoder->createShipment('mx4025', 1);
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$well = $this->encoder->addWellToPlate($plate['index'], 4, 5);
		$this->assertEquals(4, $well['rowNumber']);
		$this->assertEquals(5, $well['columnNumber']);
	}

	public function testAddWellToPlateNoPlate() {
		$this->encoder->createShipment('mx4025', 1);
		$this->expectExceptionMessageMatches('~No plate~');
		$this->encoder->addWellToPlate(1, 4, 5);
	}

	public function testAddWellToPlateTwice() {
		$this->encoder->createShipment('mx4025', 1);
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$this->encoder->addWellToPlate($plate['index'], 4, 5);
		$this->expectExceptionMessageMatches('~already exists~');
		$this->encoder->addWellToPlate($plate['index'], 4, 5);
	}

	public function testAddWellToPlateBadRowNumber() {
		$this->encoder->createShipment('mx4025', 1);
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$this->expectExceptionMessageMatches('~Row number must be between~');
		$this->encoder->addWellToPlate($plate['index'], 0, 5);
	}

	public function testAddWellToPlateBadColumnNumber() {
		$this->encoder->createShipment('mx4025', 1);
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$this->expectExceptionMessageMatches('~Column number must be between~');
		$this->encoder->addWellToPlate($plate['index'], 4, 0);
	}

	public function testAddDropToPlateWell() {
		$this->encoder->createShipment('mx4025', 1);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$well = $this->encoder->addWellToPlate($plate['index'], 4, 7);
		$ret = $this->encoder->addDropToPlateWell($well['index'], 1, 1);
		$this->assertArrayHasKey('MacromoleculeSample', $ret);
		$this->assertArrayHasKey('WellDrop', $ret);
		$this->assertEquals('#/Macromolecule/Macromolecule' . $macromolecule['index'], $ret['MacromoleculeSample']['macromoleculeRef']['$ref']);
		$this->assertEquals('BARCODE1234_D07_1', $ret['WellDrop']['name']);
		$this->assertEquals('#/PlateWell/PlateWell' . $well['index'], $ret['WellDrop']['containerRef']['$ref']);
		$this->assertEquals('#/MacromoleculeSample/MacromoleculeSample' . $ret['MacromoleculeSample']['index'], $ret['WellDrop']['sampleRef']['$ref']);
		$this->assertArrayHasKey('index', $ret['MacromoleculeSample']);
		$this->assertArrayHasKey('index', $ret['WellDrop']);
	}

	public function testAddTwoDropsToSamePlateWell() {
		$this->encoder->createShipment('mx4025', 1);
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$well = $this->encoder->addWellToPlate($plate['index'], 4, 7);
		$this->encoder->addDropToPlateWell($well['index'], 1, 1);
		$ret = $this->encoder->addDropToPlateWell($well['index'], 2, 1);
		$this->assertArrayHasKey('WellDrop', $ret);
		$this->assertArrayHasKey('MacromoleculeSample', $ret);
		$this->assertArrayHasKey('index', $ret['MacromoleculeSample']);
		$this->assertArrayHasKey('index', $ret['WellDrop']);
		$this->assertEquals('#/Macromolecule/Macromolecule' . $macromolecule['index'], $ret['MacromoleculeSample']['macromoleculeRef']['$ref']);
		$this->assertEquals('BARCODE1234_D07_2', $ret['WellDrop']['name']);
		$this->assertEquals('#/PlateWell/PlateWell' . $well['index'], $ret['WellDrop']['containerRef']['$ref']);
		$this->assertEquals('#/MacromoleculeSample/MacromoleculeSample' . $ret['MacromoleculeSample']['index'], $ret['WellDrop']['sampleRef']['$ref']);
	}

	public function testAddDropToPlateWellWithSampleName() {
		$this->encoder->createShipment('mx4025', 1);
		$this->encoder->addMacromoleculeToShipment('TEST');
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$well = $this->encoder->addWellToPlate($plate['index'], 4, 7);
		$ret = $this->encoder->addDropToPlateWell($well['index'], 1, 1, 'sampleName');
		$this->assertEquals('sampleName', $ret['WellDrop']['name']);
	}

	public function testAddDropToPlateWellNoWell() {
		$this->expectExceptionMessageMatches('~No well with index~');
		$this->encoder->addDropToPlateWell(1, 1, 1);
	}

	public function testAddDropToPlateWellNoMacromolecule() {
		$this->encoder->createShipment('mx4025', 1);
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$this->encoder->addWellToPlate($plate['index'], 4, 7);
		$this->expectExceptionMessageMatches('~No macromolecule with index~');
		$this->encoder->addDropToPlateWell(1, 1, 1);
	}

	public function testAddDropToPlateWellDuplicateDrop() {
		$this->encoder->createShipment('mx4025', 1);
		$this->encoder->addMacromoleculeToShipment('TEST');
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$this->encoder->addWellToPlate($plate['index'], 4, 7);
		$this->expectExceptionMessageMatches('~drop already exists~');
		$this->encoder->addDropToPlateWell(1, 1, 1);
		$this->encoder->addDropToPlateWell(1, 1, 1);
	}

	public function testAddDropToPlateWellBadDropNumber() {
		$this->encoder->createShipment('mx4025', 1);
		$this->encoder->addMacromoleculeToShipment('TEST');
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$this->encoder->addWellToPlate($plate['index'], 4, 7);
		$this->expectExceptionMessageMatches('~Drop number must be between~');
		$this->encoder->addDropToPlateWell(1, 6, 1);
	}

	public function testAddDropToPlateWellDuplicateSampleName() {
		$this->encoder->createShipment('mx4025', 1);
		$this->encoder->addMacromoleculeToShipment('TEST');
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$this->encoder->addWellToPlate($plate['index'], 4, 7);
		$this->expectExceptionMessageMatches('~name already exists~');
		$this->encoder->addDropToPlateWell(1, 1, 1, 'sampleName');
		$this->encoder->addDropToPlateWell(1, 2, 1, 'sampleName');
	}

	private function createPlateAndDrop(): array {
		$this->encoder->createShipment('mx4025', 1);
		$plate = $this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$well=$this->encoder->addWellToPlate($plate['index'], 4, 7);
		$macromolecule=$this->encoder->addMacromoleculeToShipment('TEST');
		$ret=$this->encoder->addDropToPlateWell($well['index'], 3, $macromolecule['index']);
		$ret['WellDrop']['plateIndex']=$plate['index'];
		$ret['WellDrop']['wellIndex']=$well['index'];
		$ret['WellDrop']['rowNumber']=$well['rowNumber'];
		$ret['WellDrop']['columnNumber']=$well['columnNumber'];
		$ret['WellDrop']['macromoleculeIndex']=$macromolecule['index'];
		return $ret['WellDrop'];
	}

	public function testAddPlatePointDropRegionByPlateDropIndex(){
		$drop=$this->createPlateAndDrop();
		$region=$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200);
		$this->assertArrayHasKey('region', $region);
		$this->assertArrayHasKey('uuid', $region);
		$this->assertArrayHasKey('index', $region);
		$this->assertEquals('DropRegion', $region['mxlimsType']);
		$this->assertEquals($this->version, $region['version']);
		$this->assertEquals('#/WellDrop/WellDrop'.$drop['index'], $region['containerRef']['$ref']);
		$this->assertEquals('micron', $region['region']['units']);
		$this->assertEquals('point', $region['region']['region']['regionType']);
		$this->assertEquals(100, $region['region']['region']['x']);
		$this->assertEquals(200, $region['region']['region']['y']);
	}

	public function testAddPlatePointDropRegionByPlateDropIndexWithMimeType(){
		$drop=$this->createPlateAndDrop();
		$this->expectExceptionMessageMatches('~Do not set image MIME type~');
		$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200, 'text/plain');
	}

	public function testAddImagePointDropRegionByPlateDropIndex(){
		$drop=$this->createPlateAndDrop();
		$region=$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200, 'image/jpeg', 'http://image.url/1234');
		$this->assertArrayHasKey('index', $region);
		$this->assertEquals('DropRegion', $region['mxlimsType']);
		$this->assertEquals($this->version, $region['version']);
		$this->assertArrayHasKey('uuid', $region);
		$this->assertEquals('#/WellDrop/WellDrop'.$drop['index'], $region['containerRef']['$ref']);
		$this->assertArrayHasKey('region', $region);
		$this->assertEquals('pixel', $region['region']['units']);
		$this->assertEquals('point', $region['region']['region']['regionType']);
		$this->assertEquals(100, $region['region']['region']['x']);
		$this->assertEquals(200, $region['region']['region']['y']);
	}

	public function testAddImagePointDropRegionNoMimeType() {
		$drop=$this->createPlateAndDrop();
		$this->expectExceptionMessageMatches('~No image MIME type~');
		$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200, null, 'http://image.url/1234');
	}

	public function testAddImagePointDropRegionBadMimeType() {
		$drop=$this->createPlateAndDrop();
		$this->expectExceptionMessageMatches('~Bad image MIME type~');
		$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200, 'text/plain', 'http://image.url/1234');
	}

	public function testAddImagePointDropRegionBothUrlAndData() {
		$drop=$this->createPlateAndDrop();
		$this->expectExceptionMessageMatches('~both imageUrl and imageData~');
		$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200, 'image/jpeg', 'http://image.url/1234', 'df2ys3dy5gd2grt7e');
	}

	public function testAddImagePointDropRegionBadUrl() {
		$drop=$this->createPlateAndDrop();
		$this->expectExceptionMessageMatches('~Bad image URL~');
		$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200, 'image/jpeg', 'http:/image.url/1234');
	}

	public function testAddImagePointDropRegionBadCoordinate() {
		$drop=$this->createPlateAndDrop();
		$this->expectExceptionMessageMatches('~cannot be negative~');
		$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, -200, 'image/jpeg', 'http://image.url/1234');
	}

	public function testAddCrystalToDropRegion() {
		$drop=$this->createPlateAndDrop();
		$region=$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200);
		$crystal=$this->encoder->addCrystalToDropRegion($region['index'], 'CRYSTAL_NAME');
		$this->assertArrayHasKey('uuid', $crystal);
		$this->assertEquals('Crystal', $crystal['mxlimsType']);
		$this->assertEquals('CRYSTAL_NAME', $crystal['name']);
		$this->assertEquals('#/DropRegion/DropRegion'.$region['index'], $crystal['containerRef']['$ref']);
		$this->assertEquals($drop['sampleRef']['$ref'], $crystal['sampleRef']['$ref']);
	}

	public function testValidateNoShipment() {
		$this->expectExceptionMessageMatches('~No shipment~');
		$this->encoder->validate();
	}

	public function testValidateNoLabContactOutbound() {
		$this->encoder->createShipment('mx4025');
		$this->expectExceptionMessageMatches('~lab contact~');
		$this->encoder->validate();
	}

	public function testValidateNoLabContactReturn() {
		$this->encoder->createShipment('mx4025');
		$this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->expectExceptionMessageMatches('~lab contact~');
		$this->encoder->validate();
	}

	public function testValidateNoDewarsOrPlates() {
		$this->encoder->createShipment('mx4025');
		$this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->encoder->setLabContactReturn('Bob', 'bob@bob.com');
		$this->expectExceptionMessageMatches('~Dewars or Plates~');
		$this->encoder->validate();
	}

	public function testValidateSinglePositionPinButNoSamples() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->encoder->setLabContactReturn('Bob', 'bob@bob.com');
		$this->encoder->addSinglePositionPinToPuck($puck['index'], 4, 'PIN1');
		$this->encoder->addMacromoleculeToShipment('TEST');
		$this->expectExceptionMessageMatches('~No MacromoleculeSamples~');
		$this->encoder->validate();
	}

	public function testValidateMultiPositionPinButNoSamples() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->encoder->setLabContactReturn('Bob', 'bob@bob.com');
		$this->encoder->addMultiPositionPinToPuck($puck['index'], 4, 8, 'MULTIPIN1');
		$this->encoder->addMacromoleculeToShipment('TEST');
		$this->expectExceptionMessageMatches('~No PinPositions~');
		$this->encoder->validate();
	}

	public function testValidatePlateButNoWells(){
		$this->encoder->createShipment('mx4025');
		$this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->encoder->setLabContactReturn('Bob', 'bob@bob.com');
		$this->encoder->addMacromoleculeToShipment('TEST');
		$this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$this->expectExceptionMessageMatches('~No PlateWells~');
		$this->encoder->validate();
	}

	public function testValidatePlateWellButNoDrops(){
		$this->encoder->createShipment('mx4025');
		$this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->encoder->setLabContactReturn('Bob', 'bob@bob.com');
		$this->encoder->addMacromoleculeToShipment('TEST');
		$plate=$this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$this->encoder->addWellToPlate($plate['index'], 1, 1);
		$this->expectExceptionMessageMatches('~No WellDrops~');
		$this->encoder->validate();
	}

	public function testValidatePlateButNoDropRegions(){
		$this->encoder->createShipment('mx4025');
		$macromolecule=$this->encoder->addMacromoleculeToShipment('TEST');
		$this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->encoder->setLabContactReturn('Bob', 'bob@bob.com');
		$plate=$this->encoder->addPlateToShipment('BARCODE1234', 8, 12, 3);
		$well=$this->encoder->addWellToPlate($plate['index'], 1, 1);
		$this->encoder->addDropToPlateWell($well['index'], 1, $macromolecule['index']);
		$this->expectExceptionMessageMatches('~No DropRegions~');
		$this->encoder->validate();
	}

	public function testValidateDropRegionButNoCrystal(){
		$drop=$this->createPlateAndDrop();
		$this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->encoder->setLabContactReturn('Bob', 'bob@bob.com');
		$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200);
		$this->expectExceptionMessageMatches('~No crystal~');
		$this->encoder->validate();
	}

	public function testValidateValidPlateShipment() {
		$drop=$this->createPlateAndDrop();
		$this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->encoder->setLabContactReturn('Bob', 'bob@bob.com');
		$region=$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200);
		$this->encoder->addCrystalToDropRegion($region['index'], 'CRYSTAL_NAME');
		$result=$this->encoder->validate();
		self::assertTrue($result);
	}

	public function testValidateDewarButNoPucks() {
		$this->encoder->createShipment('mx4025');
		$this->encoder->setLabContactOutbound('Bob','bob@bob.com');
		$this->encoder->setLabContactReturn('Bob','bob@bob.com');
		$this->encoder->addDewarToShipment('DLS-MX-1234');
		$this->encoder->addMacromoleculeToShipment('TEST');
		$this->expectExceptionMessageMatches('~No Pucks~');
		$this->encoder->validate();
	}

	public function testValidateNoMacromolecules() {
		$this->encoder->createShipment('mx4025');
		$this->encoder->setLabContactOutbound('Bob','bob@bob.com');
		$this->encoder->setLabContactReturn('Bob','bob@bob.com');
		$this->encoder->addDewarToShipment('DLS-MX-1234');
		$this->encoder->addPuckToDewar(1, 'OUL-999', 16);
		$this->expectExceptionMessageMatches('~No Macromolecules~');
		$this->encoder->validate();
	}

	public function testValidateNoPinsOrMultiPins() {
		$this->encoder->createShipment('mx4025');
		$this->encoder->setLabContactOutbound('Bob','bob@bob.com');
		$this->encoder->setLabContactReturn('Bob','bob@bob.com');
		$this->encoder->addDewarToShipment('DLS-MX-1234');
		$this->encoder->addPuckToDewar(1, 'OUL-999', 16);
		$this->encoder->addMacromoleculeToShipment('TEST');
		$this->expectExceptionMessageMatches('~No Pins or MultiPins~');
		$this->encoder->validate();
	}

	/**
	 * @param $json
	 * @return void
	 * @throws \Exception
	 */
	private function validateJsonAgainstSchema($json): void {
		$command=@file_get_contents(__DIR__.'/SchemaValidationCommand');
		if(!$command){ $this->markTestSkipped('No SchemaValidationCommand file found'); }

		$encoderVersion=$this->encoder->getVersion();
		$objectSchema=@file_get_contents(__DIR__.'/../../../../schemas/data/MxlimsObjectData.json');
		if(!$objectSchema){
			throw new \Exception('Could not open ShipmentMessage schema to determine version number');
		}
		$objectSchema=json_decode($objectSchema, true);
		if(!$objectSchema){
			throw new \Exception('Could not parse ShipmentMessage schema');
		}
		$schemaVersion=$objectSchema['properties']['version']['const'];
		if($schemaVersion!==$encoderVersion){
			$this->markTestSkipped("Version mismatch: Local MXLIMS schema copy $schemaVersion does not match generated shipment $encoderVersion. Cannot validate against schema.");
		}

		$jsonPath=str_replace('/', DIRECTORY_SEPARATOR,__DIR__.'/test.json');
		$schemaPath=str_replace('/', DIRECTORY_SEPARATOR,__DIR__.'/../../../../schemas/messages/ShipmentMessage.json');
		if(!@file_put_contents($jsonPath, $json)){
			$this->fail('Could not write test JSON to disk for parsing');
		}
		$command=str_replace('{{$jsonFile}}', $jsonPath, $command);
		$command=str_replace('{{$schemaFile}}', $schemaPath, $command);
		$result=(exec($command));
		$acceptableResults=['True'];
		if(!in_array($result, $acceptableResults)){
			echo $json;
		}
		$this->assertContains($result, $acceptableResults);
	}

	/**
	 * @throws \Exception
	 */
	public function testSinglePinJsonValidatesAgainstSchema() {
		$this->encoder->createShipment('mx4025', 4);
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$macromolecule=$this->encoder->addMacromoleculeToShipment("TEST");
		$this->encoder->addSinglePinSampleToPuck($puck['index'], 1, $macromolecule['index'], 'TEST_9098A01d1c1', 'HA00AA5432');
		$this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->encoder->setLabContactReturn('Bob', 'bob@bob.com');
		$json=$this->encoder->encodeToJSON();
		$this->validateJsonAgainstSchema($json);
	}

	/**
	 * @throws \Exception
	 */
	public function testMultiPinJsonValidatesAgainstSchema() {
		$this->encoder->createShipment('mx4025', 4);
		$this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->encoder->setLabContactReturn('Bob', 'bob@bob.com');
		$dewar = $this->encoder->addDewarToShipment('DLS-MX-1234');
		$puck = $this->encoder->addPuckToDewar($dewar['index'], 'OUL-999', 16);
		$pin = $this->encoder->addMultiPositionPinToPuck($puck['index'], 10, 8, 'MULTIPIN1');
		$macromolecule = $this->encoder->addMacromoleculeToShipment('TEST');
		$this->encoder->addSampleToMultiPositionPin($pin['index'], 1, $macromolecule['index'], 'TEST_9098A01d1c1');
		$json=$this->encoder->encodeToJSON();
		$this->validateJsonAgainstSchema($json);
	}

	/**
	 * @throws \Exception
	 */
	public function testPlateJsonValidatesAgainstSchema() {
		$drop=$this->createPlateAndDrop();
		$this->encoder->setLabContactOutbound('Bob', 'bob@bob.com');
		$this->encoder->setLabContactReturn('Bob', 'bob@bob.com');
		$region=$this->encoder->addPointDropRegionByPlateDropIndex($drop['index'], 100, 200);
		$this->encoder->addCrystalToDropRegion($region['index'], 'CRYSTAL_NAME');
		$json=$this->encoder->encodeToJSON(true);
		$this->validateJsonAgainstSchema($json);
	}

}