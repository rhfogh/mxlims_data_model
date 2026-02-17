<?php
namespace mxlims\tools\php\src\ShipmentEncoder;

use Exception;

interface ShipmentEncoderInterface {

	/**
	 * Returns the MXLIMS version.
	 * @return string The MXLIMS version.
	 */
	public function getVersion(): string;

	/**
	 * Gets an object in the shipment message, by its MXLIMS type and its (1-based) index).
	 * @param string $mxlimsType The MXLIMS type.
	 * @param int $index The index.
	 * @return array|null The MXLIMS object, or null if not found.
	 */
	public function get(string $mxlimsType, int $index): ?array;

	/**
	 * Gets an object in the shipment message by its JSON path.
	 * @param string|array $path. Either a path in the form "#/ObjectType/ObjectType123", or an array with a $ref property whose value is a JSON path in that form.
	 * @throws Exception
	 */
	public function getByJsonPath(string|array $path): ?array;

	/**
	 * Creates the basic shipment to which everything else will be added.
	 * @param string $proposalCode The name of the proposal at the synchrotron (e.g., "mx4025").
	 * @param int|null $sessionNumber The number of the session within the proposal, or null for unattended/mail-in collection.
	 * @param string|null $uuid The UUID for the shipment. If not provided, this will be generated automatically.
	 * @return array The shipment.
	 * @throws Exception if $proposalName isn't alphanumeric.
	 */
	public function createShipment(string $proposalCode, int $sessionNumber=null, string $uuid=null): array;

	/**
	 * Sets and returns the outbound lab contact for the shipment.
	 * @param string $name The lab contact's name.
	 * @param string|null $emailAddress The lab contact's email address.
	 * @param string|null $phoneNumber The lab contact's phone number.
	 * @return array The lab contact.
	 * @throws Exception if name is empty, or if both email address and phone number are empty.
	 */
	public function setLabContactOutbound(string $name, string $emailAddress=null, string $phoneNumber=null): array;

	/**
	 * Sets and returns the return lab contact for the shipment.
	 * @param string $name The lab contact's name.
	 * @param string|null $emailAddress The lab contact's email address.
	 * @param string|null $phoneNumber The lab contact's phone number.
	 * @return array The lab contact.
	 * @throws Exception if name is empty, or if both email address and phone number are empty.
	 */
	public function setLabContactReturn(string $name, string $emailAddress=null, string $phoneNumber=null): array;

	/**
	 * Adds a macromolecule to the shipment.
	 * @param string $acronym The protein acronym (which identifies the macromolecule in the synchrotron's safety systems).
	 * @param string|null $uuid A pre-existing UUID for this macromolecule. If not supplied, one will be generated.
	 * @throws Exception if the acronym is empty.
	 */
	public function addMacromoleculeToShipment(string $acronym, ?string $uuid=null): array;

	/**
	 * Adds a dewar to the shipment.
	 * @param string|null $barcode The dewar barcode.
	 * @param string|null $uuid An existing UUID for the dewar. If not supplied, one will be generated.
	 * @return array
	 * @throws Exception if there are Plates in the Shipment
	 */
	public function addDewarToShipment(string $barcode=null, ?string $uuid=null): array;

	/**
	 * Adds a puck to a dewar.
	 * @param int $dewarIndex The index of the dewar within the shipment message. This is the "index" property of the object returned from addDewarToShipment.
	 * @param string $barcode The puck barcode.
	 * @param int $numPositions The number of pin positions in the puck.
	 * @param string|null $uuid An existing UUID for the puck. If not supplied, one will be generated.
	 * @return array The puck.
	 * @throws Exception if the dewar cannot be found, or if $numPositions is not positive.
	 */
	public function addPuckToDewar(int $dewarIndex, string $barcode, int $numPositions, ?string $uuid=null): array;

	/**
	 * Adds a frozen crystal on a traditional loop, creating both Pin and MacromoleculeSample objects.
	 * @param int $puckIndex The (1-based) index of the Puck within the top-level array).
	 * @param int $puckPosition The (1-based) position of the pin within the puck.
	 * @param int $macromoleculeIndex The (1-based) index of the sample's Macromolecule within the top-level array).
	 * @param string $sampleName The name of the sample.
	 * @param string|null $pinBarcode The barcode of the pin.
	 * @param string|null $pinUuid An existing UUID for the pin. If not specified, one will be generated.
	 * @param string|null $sampleUuid An existing UUID for the sample. If not specified, one will be generated.
	 * @return array An array containing the sample and the pin.
	 * @throws Exception if the specified Puck or Macromolecule do not exist.
	 * @throws Exception if there are already multi-position pins in the shipment.
	 * @throws Exception if the puck position is out of range.
	 * @throws Exception if the position is already occupied.
	 */
	public function addSinglePinSampleToPuck(int $puckIndex, int $puckPosition, int $macromoleculeIndex, string $sampleName, ?string $pinBarcode=null, ?string $pinUuid=null, ?string $sampleUuid=null): array;

	/**
	 * Adds a single-position pin (such as a traditional loop) to a puck.
	 * @param int $puckIndex The (1-based) index of the Puck within the top-level Puck array.
	 * @param int $puckPosition The (1-based) position within the puck.
	 * @param string|null $barcode The pin barcode.
	 * @param string|null $uuid A previously-set UUID for the pin; if not supplied, one will be generated.
	 * @return array The pin.
	 * @throws Exception if shipment already contains a multi-position pin.
	 * @throws Exception if puck does not exist in shipment.
	 * @throws Exception if number of pin positions is not a positive integer.
	 * @throws Exception if position in puck is out of range, or already filled.
	 */
	public function addSinglePositionPinToPuck(int $puckIndex, int $puckPosition, ?string $barcode=null, ?string $uuid=null): array;

	/**
	 * Adds a multi-position pin to a puck.
	 * @param int $puckIndex The (1-based) index of the Puck within the top-level Puck array.
	 * @param int $puckPosition The (1-based) position within the puck.
	 * @param int $numPositions How many sample positions the pin has.
	 * @param string|null $barcode The pin barcode.
	 * @param string|null $uuid A previously-set UUID for the pin; if not supplied, one will be generated.
	 * @return array The pin.
	 * @throws Exception if shipment already contains a single-position pin.
	 * @throws Exception if puck does not exist in shipment.
	 * @throws Exception if number of pin positions is not a positive integer.
	 * @throws Exception if position in puck is out of range, or already filled.
	 */
	public function addMultiPositionPinToPuck(int $puckIndex, int $puckPosition, int $numPositions, ?string $barcode=null, ?string $uuid=null): array;

	/**
	 * Adds a sample to a multi-position pin.
	 * @param int $pinIndex The index of the pin.
	 * @param int $pinPosition The position within the pin.
	 * @param int $macromoleculeIndex The index of the macromolecule.
	 * @param string $sampleName The name of the sample.
	 * @param string|null $sampleUuid An existing UUID for the sample. If not supplied, one will be generated.
	 * @return array An array containing the PinPosition and MacromoleculeSample.
	 * @throws Exception if pin or macromolecule does not exist.
	 * @throws Exception if pin position is already filled.
	 * @throws Exception if sample name already exists.
	 */
	public function addSampleToMultiPositionPin(int $pinIndex, int $pinPosition, int $macromoleculeIndex, string $sampleName, string $sampleUuid=null): array;

	/**
	 * Adds a plate to the shipment.
	 * @param string $barcode The plate barcode.
	 * @param int $rows The number of rows in the plate.
	 * @param int $columns The number of columns in the plate.
	 * @param int $subPositions The number of sub-positions in each well of the plate.
	 * @param string|null $dropMapping A string describing the sender's mapping of drop numbers to well sub-positions. By default, this places drops above the reservoir in increasing drop number order from left to right.
	 * @param string|null $uuid An existing UUID for the plate. If not provided, one will be generated.
	 * @return array The plate.
	 * @throws Exception if barcode is not provided.
	 * @throws Exception if there is a Dewar in the shipment.
	 * @throws Exception if $rows, $columns or $subPositions are not positive integers.
	 */
	public function addPlateToShipment(string $barcode, int $rows, int $columns, int $subPositions, ?string $dropMapping=null, ?string $uuid = null): array;

	/**
	 * @param int $plateIndex The index of the plate.
	 * @param int $rowNumber The row number of the well.
	 * @param int $columnNumber The column number of the well.
	 * @param string|null $uuid An existing UUID for the well; if not provided, one will be generated.
	 * @return array The well.
	 * @throws Exception if the plate does not exist.
	 * @throws Exception if $rowNumber or $columnNumber are out of range for the plate type.
	 * @throws Exception if a well at this plate position already exists.
	 */
	public function addWellToPlate(int $plateIndex, int $rowNumber, int $columnNumber, ?string $uuid=null): array;

	/**
	 * Adds a drop to the plate well, creating a MacromoleculeSample.
	 * @param int $wellIndex The index of the plate well.
	 * @param int $dropNumber The number of the sub-position within the plate well.
	 * @param int $macromoleculeIndex The index of the macromolecule.
	 * @param string|null $name The name of the drop. Default is, e.g., "BARCODE_A01_3" for a drop in sub-position 3 of the top left well of plate with barcode "BARCODE".
	 * @param string|null $uuid An existing UUID for the well. If not supplied, one will be generated.
	 * @return array An array containing WellDrop and MacromoleculeSample.
	 * @throws Exception if there is no well with the specified index.
	 * @throws Exception if there is no macromolecule with the specified index.
	 * @throws Exception if the drop number is out of range for the plate type.
	 * @throws Exception if the well drop already exists.
	 * @throws Exception if the name already exists.
	 */
	public function addDropToPlateWell(int $wellIndex, int $dropNumber, int $macromoleculeIndex, ?string $name=null, ?string $uuid=null): array;

	/**
	 * Gets the plate well in the specified plate, with the specified row and column number.
	 * @param int $plateIndex
	 * @param int $rowNumber
	 * @param int $columnNumber
	 * @return array|null
	 * @throws Exception if no plate with index $plateIndex is found.
	 */
	public function getPlateWellByPosition(int $plateIndex, int $rowNumber, int $columnNumber): ?array;

	/**
	 * Gets the well drop in the specified plate, with the specified row, column and sub-position (drop) number.
	 * @param int $plateIndex
	 * @param int $rowNumber
	 * @param int $columnNumber
	 * @param int $dropNumber
	 * @return array|null
	 * @throws Exception if no plate with index $plateIndex is found.
	 */
	public function getWellDropByPosition(int $plateIndex, int $rowNumber, int $columnNumber, int $dropNumber): ?array;


	/**
	 * Adds a point region. This may be either a plate region (defined relative to a fiducial mark) or an image region (defined
	 *  as pixel co-ordinates on a supplied image).
	 *
	 * For plate regions: Leave $imageMimeType, $imageUrl and $imageData null. Co-ordinate units are assumed to be microns.
	 *
	 * For image regions. Specify $imageMimeType AND ($imageUrl XOR $imageData). Co-ordinate units are assumed to be pixels.
	 * @param int $dropIndex
	 * @param int $x The X co-ordinate
	 * @param int $y The Y co-ordinate
	 * @param string|null $imageMimeType
	 * @param string|null $imageUrl
	 * @param string|null $imageData
	 * @return array
	 * @throws Exception if $x or $y is negative, or if addDropRegion throws an Exception.
	 */
	public function addPointDropRegionByPlateDropIndex(int $dropIndex, int $x, int $y, ?string $imageMimeType=null, ?string $imageUrl=null, ?string $imageData=null): array;

	/**
	 * Adds a crystal and associates it with an existing drop region in the shipment.
	 * @param int $dropRegionIndex The index of the drop region marking this crystal.
	 * @param string $name The name of the crystal.
	 * @param string|null $uuid An existing UUID for the crystal. If not specified, one will be generated.
	 * @return array The crystal object.
	 * @throws Exception if the specified drop region does not exist in the shipment.
	 */
	public function addCrystalToDropRegion(int $dropRegionIndex, string $name, ?string $uuid=null): array;

	/**
	 * Validates the shipment.
	 * @return bool true if shipment is valid.
	 * @throws Exception if shipment is not valid - see the exception message for details.
	 */
	public function validate(): bool;

	/**
	 * Returns an MXLIMS-formatted ShipmentMessage.
	 * @param bool $prettyPrint Whether to format the JSON to make it more human-readable.
	 * @return string The shipment, encoded as JSON in MXLIMS format.
	 * @throws Exception if shipment does not validate.
	 */
	public function encodeToJson(bool $prettyPrint=false): string;
}