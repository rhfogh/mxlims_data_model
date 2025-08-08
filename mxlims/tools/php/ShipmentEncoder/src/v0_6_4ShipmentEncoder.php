<?php

namespace mxlims\tools\php\ShipmentEncoder\src;

include_once __DIR__.'/ShipmentEncoderInterface.php';

class v0_6_4ShipmentEncoder implements ShipmentEncoderInterface {

	/**
	 * @var string $plateRowLabels Used to generate plate well/drop names, with A being the top row of a plate, B the next, etc.
	 */
	public string $plateRowLabels='-ABCDEFGHIJKLMNOPQRSTUVWXYZ';

	/**
	 * @var array $shipmentMessage The shipment message will be built up here
	 */
	public array $shipmentMessage;

	/**
	 * Returns an array with the basic "mxlimsType", "version", and "uuid" parameters, generating the UUID if not supplied.
	 * @param string $mxlimsType The type of object.
	 * @param string|null $uuid A pre-existing UUID for the object. If not supplied, one will be generated.
	 * @return array The base object.
	 * @throws \Exception if $mxlimsType is not alphanumeric or does not start with a capital letter
	 */
	public function getBaseObject(string $mxlimsType, ?string $uuid=null): array {
		if(!preg_match('/^[A-Z][a-zA-Z0-9]+$/', $mxlimsType)){
			throw new \Exception("Bad mxlimsType $mxlimsType");
		}
		if(!$uuid){
			$uuid=$this->generateUuid();
		}
		return [
			'mxlimsType' => $mxlimsType,
			'version' => $this->getVersion(),
			'uuid' => $uuid
		];
	}

	/**
	 * Generates a UUIDv7.
	 * @return string the UUID.
	 */
	public function generateUuid(): string {
		$timestamp = intval(microtime(true) * 1000);
		return strtolower(sprintf('%02x%02x%02x%02x-%02x%02x-%04x-%04x-%012x',
			// first 48 bits are timestamp based
			($timestamp >> 40) & 0xFF,
			($timestamp >> 32) & 0xFF,
			($timestamp >> 24) & 0xFF,
			($timestamp >> 16) & 0xFF,
			($timestamp >> 8) & 0xFF,
			$timestamp & 0xFF,

			// 16 bits: 4 bits for version (7) and 12 bits for rand_a
			mt_rand(0, 0x0FFF) | 0x7000,

			// 16 bits: 4 bits for variant where 2 bits are fixed 10 and next 2 are random to get (8-9, a-b)
			// next 12 are random
			mt_rand(0, 0x3FFF) | 0x8000,
			// random 48 bits
			mt_rand(0, 0xFFFFFFFFFFFF),
		));
	}

	/**
	 * @see ShipmentEncoderInterface::getVersion()
	 */
	public function getVersion(): string {
		if(isset($this->version)){
			return $this->version;
		}
		$parts=explode('\\', get_called_class());
		$className=end($parts);
		if(!preg_match('/\d+_\d+_\d+/', $className, $matches)){
			throw new \Exception('Cannot determine version from class name');
		}
		$version=str_replace('_','.',$matches[0]);
		$this->version=$version;
		return $this->version;
	}

	/**
	 * @see ShipmentEncoderInterface::get()
	 */
	public function get(string $mxlimsType, int $index): ?array {
		if(isset($this->shipmentMessage[$mxlimsType][$mxlimsType.$index])){
			$obj=$this->shipmentMessage[$mxlimsType][$mxlimsType.$index];
			$obj['index']=$index;
			return $obj;
		}
		return null;
	}

	/**
	 * @see ShipmentEncoderInterface::getByJsonPath()
	 * @throws \Exception
	 */
	public function getByJsonPath(string|array $path): ?array {
		if(is_array($path)){
			if(isset($path['$ref'])){
				$path=$path['$ref'];
			} else {
				throw new \Exception('No $ref property');
			}
		}
		if (!str_starts_with($path,'#/')) {
			throw new \Exception('JSON path must start with #/');
		}
		$path = substr($path, 2);
		$parts = explode('/', $path);
		if (2 !== count($parts)) {
			throw new \Exception('Too many parts in JSON path');
		}
		if (!str_starts_with($parts[1], $parts[0]) && !(int)substr($parts[1], strlen($parts[0]))) {
			throw new \Exception('JSON path must be in the form #/ObjectType/ObjectType123');
		}
		$index=(int)substr($parts[1], strlen($parts[0]));
		return $this->get($parts[0], $index);
	}

	/**
	 * @see ShipmentEncoderInterface::createShipment()
	 * @throws \Exception
	 */
	public function createShipment(string $proposalCode, ?int $sessionNumber=null, ?string $uuid=null): array {
		if(!empty($this->shipmentMessage)){
			throw new \Exception("Shipment already added to message");
		}
		if(!preg_match('/^[0-9A-Za-z]+$/', $proposalCode)){
			throw new \Exception("Bad proposal code $proposalCode");
		}
		$shipment=$this->getBaseObject('Shipment', $uuid);
		$shipment['proposalCode']=$proposalCode;
		if($sessionNumber){
			if($sessionNumber<1){
				throw new \Exception("Session number must be a positive number");
			}
			$shipment['sessionNumber'] = $sessionNumber;
		}
		$this->shipmentMessage=[];
		$this->setObjectToMessage($shipment);
		return $shipment;
	}

	/**
	 * @see ShipmentEncoderInterface::setLabContactOutbound()
	 * @throws \Exception
	 */
	public function setLabContactOutbound(string $name, ?string $emailAddress=null, ?string $phoneNumber=null): array {
		return $this->setLabContact('Outbound', $name, $emailAddress, $phoneNumber);
	}

	/**
	 * @see ShipmentEncoderInterface::setLabContactReturn()
	 * @throws \Exception
	 */
	public function setLabContactReturn(string $name, ?string $emailAddress=null, ?string $phoneNumber=null): array {
		return $this->setLabContact('Return', $name, $emailAddress, $phoneNumber);
	}

	/**
	 * @see ShipmentEncoderInterface::addMacromoleculeToShipment()
	 * @throws \Exception
	 */
	public function addMacromoleculeToShipment(string $acronym, ?string $uuid=null): array {
		if(empty($acronym)){
			throw new \Exception('Acronym cannot be empty.');
		}
		$macromolecule=$this->getBaseObject('Macromolecule', $uuid);
		$macromolecule['acronym']=$acronym;
		$this->setObjectToMessage($macromolecule);
		return $macromolecule;
	}


	/**
	 * Sets and returns the lab contact.
	 * @param string $direction Whether this is the Outbound or Return lab contact.
	 * @param string $name The lab contact's name.
	 * @param string|null $emailAddress The lab contact's email address.
	 * @param string|null $phoneNumber The lab contact's phone number.
	 * @return array The lab contact.
	 * @throws \Exception if name is empty, or if both email address and phone number are empty.
	 * @throws \Exception if direction is not "Outbound" or "Return".
	 * */
	public function setLabContact(string $direction, string $name, ?string $emailAddress, ?string $phoneNumber): array {
		if('Outbound'!==$direction && 'Return'!==$direction){ throw new \Exception('Bad lab contact direction'); }
		if(empty($name)){ throw new \Exception("Name cannot be empty"); }
		if(empty($emailAddress) && empty($phoneNumber)){ throw new \Exception("Email or phone number must be provided"); }
		$labContact=[ 'name'=>$name ];
		if($phoneNumber){ $labContact['phoneNumber']=$phoneNumber; }
		if($emailAddress){ $labContact['emailAddress']=$emailAddress; }
		$this->shipmentMessage['Shipment']['Shipment1']['labContact'.$direction]=$labContact;
		return $labContact;
	}

	/**
	 * Adds the supplied object to the shipment message, and adds an 'index' parameter indicating its (1-based) position
	 * in the top-level array. The first Dewar, for example, will be added at #/Dewar/Dewar1 and will have "index":1.
	 * @param $object array The object to add.
	 * @return void
	 */
	public function setObjectToMessage(array &$object): void {
		$type=$object['mxlimsType'];
		if(!isset($this->shipmentMessage[$type])){
			$this->shipmentMessage[$type]=[];
		}
		$index=count($this->shipmentMessage[$type])+1;
		$this->shipmentMessage[$type][$type.$index]=$object;
		$object['index']=$index;
	}

	/**
	 * @see ShipmentEncoderInterface::addDewarToShipment()
	 * @throws \Exception
	 */
	public function addDewarToShipment(?string $barcode = null, ?string $uuid = null): array {
		if(!isset($this->shipmentMessage['Shipment'])){
			throw new \Exception("Call createShipment() before addDewarToShipment()");
		}
		if(array_key_exists("Plate", $this->shipmentMessage)){
			throw new \Exception("Shipment contains Plates, cannot add Dewar");
		}
		$dewar=$this->getBaseObject('Dewar', $uuid);
		if(!empty($barcode)){
			$dewar['barcode']=$barcode;
		}
		$dewar['containerRef']=['$ref'=>'#/Shipment/Shipment1'];
		$this->setObjectToMessage($dewar);
		return $dewar;
	}

	/**
	 * @see ShipmentEncoderInterface::addPuckToDewar()
	 * @throws \Exception
	 */
	public function addPuckToDewar(int $dewarIndex, string $barcode, int $numPositions, string $uuid = null): array {
		if(!$this->get('Dewar',$dewarIndex)){
			throw new \Exception("No dewar with index $dewarIndex");
		}
		if($numPositions<1){ throw new \Exception("Number of positions must be a positive integer"); }
		$puck=$this->getBaseObject('Puck', $uuid);
		$puck['containerRef']=['$ref'=>'#/Dewar/Dewar'.$dewarIndex];
		$puck['numberPositions']=$numPositions;
		$puck['barcode']=$barcode;
		$this->setObjectToMessage($puck);
		return $puck;
	}

	/**
	 * @see ShipmentEncoderInterface::addSinglePinSampleToPuck()
	 * @throws \Exception
	 */
	public function addSinglePinSampleToPuck(int $puckIndex, int $puckPosition, int $macromoleculeIndex, string $sampleName, ?string $pinBarcode=null, ?string $pinUuid=null, ?string $sampleUuid=null): array {
		$puck=$this->get('Puck',$puckIndex);
		if(isset($this->shipmentMessage['MultiPin'])){ throw new \Exception("Cannot mix multi-position pins and traditional loops"); }
		if(!$puck){ throw new \Exception("No puck with index $puckIndex"); }
		if(!$this->get('Macromolecule',$macromoleculeIndex)){ throw new \Exception("No macromolecule with index $macromoleculeIndex"); }
		if($puckPosition<1 || $puckPosition>$puck['numberPositions']){ throw new \Exception("Puck position must be between 1 and {$puck['numberPositions']}"); }
		if(isset($this->shipmentMessage['Pin'])){
			foreach($this->shipmentMessage['Pin'] as $pin){
				if($pin['positionInPuck']===$puckPosition && $pin['containerRef']['$ref']==='#/Puck/Puck'.$puckIndex){
					throw new \Exception("Puck index $puckIndex position $puckPosition is already filled");
				}
				if(!empty($pinBarcode) && $pinBarcode===$pin['barcode']){
					throw new \Exception('Shipment already contains a pin with barcode '.$pinBarcode);
				}
			}
		}
		if(isset($this->shipmentMessage['MacromoleculeSample'])){
			foreach($this->shipmentMessage['MacromoleculeSample'] as $sample){
				if($sampleName===$sample['name']){
					throw new \Exception('Shipment already contains a sample with name '.$pinBarcode);
				}
			}
		}
		$pin=$this->getBaseObject('Pin', $pinUuid);
		if(!empty($pinBarcode)){ $pin['barcode']=$pinBarcode; }
		$sample=$this->getBaseObject('MacromoleculeSample', $sampleUuid);
		$sample['macromoleculeRef']=['$ref'=>'#/Macromolecule/Macromolecule'.$macromoleculeIndex];
		$sample['name']=$sampleName;
		$this->setObjectToMessage($sample);
		$pin['positionInPuck']=$puckPosition;
		$pin['containerRef']['$ref']='#/Puck/Puck'.$puckIndex;
		$pin['sampleRef']['$ref']='#/MacromoleculeSample/MacromoleculeSample'.$sample['index'];
		$this->setObjectToMessage($pin);
		return [
			'MacromoleculeSample'=>$sample,
			'Pin'=>$pin
		];
	}

	/**
	 * @see ShipmentEncoderInterface::addSinglePositionPinToPuck()
	 * @throws \Exception
	 */
	public function addSinglePositionPinToPuck(int $puckIndex, int $puckPosition, ?string $barcode=null, ?string $uuid=null, ?string $sampleUuid=null): array {
		$puck=$this->get('Puck',$puckIndex);
		if(isset($this->shipmentMessage['MultiPin'])){
			throw new \Exception('Shipment contains multi-position pin. Cannot add single-position pins.');
		}
		if(!$puck){
			throw new \Exception("No puck with index $puckIndex");
		}
		$puckPositions=$puck['numberPositions'];
		if($puckPosition<1 || $puckPosition>$puckPositions){
			throw new \Exception("Position in puck must be between 1 and $puckPositions");
		}
		$pin=$this->getBaseObject('Pin', $uuid);
		$pin['positionInPuck']=$puckPosition;
		$pin['containerRef']=['$ref'=>'#/Puck/Puck'.$puckIndex];
		if(!empty($barcode)){
			$pin['barcode']=$barcode;
		}
		if(isset($this->shipmentMessage['Pin'])){
			foreach($this->shipmentMessage['Pin'] as $existing){
				if($existing['containerRef']['$ref']==='#/Puck/Puck'.$puckIndex && $existing['positionInPuck']===$puckPosition){
					throw new \Exception('Puck position is already filled');
				}
			}
		}
		$this->setObjectToMessage($pin);
		return $pin;
	}

	/**
	 * @see ShipmentEncoderInterface::addMultiPositionPinToPuck()
	 * @throws \Exception
	 */
	public function addMultiPositionPinToPuck(int $puckIndex, int $puckPosition, int $numPositions, ?string $barcode=null, ?string $uuid=null): array {
		$puck=$this->get('Puck',$puckIndex);
		if(isset($this->shipmentMessage['Pin'])){
			throw new \Exception('Shipment contains single-position pin. Cannot add multi-position pins.');
		}
		if(!$puck){
			throw new \Exception("No puck with index $puckIndex");
		}
		if($numPositions<1){
			throw new \Exception('Number of positions must be a positive integer');
		}
		$puckPositions=$puck['numberPositions'];
		if($puckPosition<1 || $puckPosition>$puckPositions){
			throw new \Exception("Position in puck must be between 1 and $puckPositions");
		}
		$pin=$this->getBaseObject('MultiPin', $uuid);
		$pin['positionInPuck']=$puckPosition;
		$pin['numberPositions']=$numPositions;
		$pin['containerRef']=['$ref'=>'#/Puck/Puck'.$puckIndex];
		if(!empty($barcode)){
			$pin['barcode']=$barcode;
		}
		if(isset($this->shipmentMessage['MultiPin'])){
			foreach($this->shipmentMessage['MultiPin'] as $existing){
				if($existing['containerRef']['$ref']==='#/Puck/Puck'.$puckIndex && $existing['positionInPuck']===$puckPosition){
					throw new \Exception('Puck position is already filled');
				}
			}
		}
		$this->setObjectToMessage($pin);
		return $pin;
	}

	/**
	 * @see ShipmentEncoderInterface::addSampleToMultiPositionPin()
	 * @throws \Exception
	 */
	public function addSampleToMultiPositionPin(int $pinIndex, int $pinPosition, int $macromoleculeIndex, string $sampleName, ?string $sampleUuid=null): array {
		if(!$this->get('MultiPin',$pinIndex)){
			throw new \Exception('No pin with index '.$pinIndex);
		}
		if(!$this->get('Macromolecule',$macromoleculeIndex)){
			throw new \Exception('No macromolecule with index '.$pinIndex);
		}
		if(isset($this->shipmentMessage['PinPosition'])){
			foreach ($this->shipmentMessage['PinPosition'] as $existing){
				if($existing['positionInPin']===$pinPosition && $existing['containerRef']['$ref']==='#/MultiPin/MultiPin'.$pinIndex){
					throw new \Exception('Pin position is already filled');
				}
			}
		}
		if(isset($this->shipmentMessage['MacromoleculeSample'])){
			foreach ($this->shipmentMessage['MacromoleculeSample'] as $existing){
				if($existing['name']===$sampleName){
					throw new \Exception('Sample name already exists in shipment');
				}
			}
		}
		$sample=$this->getBaseObject('MacromoleculeSample', $sampleUuid);
		$sample['macromoleculeRef']=['$ref'=>'#/Macromolecule/Macromolecule'.$macromoleculeIndex];
		$sample['name']=$sampleName;
		$this->setObjectToMessage($sample);
		$position=$this->getBaseObject('PinPosition');
		$position['containerRef']=['$ref'=>'#/MultiPin/MultiPin'.$pinIndex];
		$position['sampleRef']=['$ref'=>'#/MacromoleculeSample/MacromoleculeSample'.$sample['index']];
		$position['positionInPin']=$pinPosition;
		$this->setObjectToMessage($position);
		return [
			'MacromoleculeSample'=>$sample,
			'PinPosition'=>$position
		];
	}

	/**
	 * @see ShipmentEncoderInterface::addPlateToShipment()
	 * @throws \Exception
	 */
	public function addPlateToShipment(string $barcode, int $rows, int $columns, int $subPositions, ?string $dropMapping=null, ?string $uuid = null): array {
		if(!isset($this->shipmentMessage['Shipment'])){
			throw new \Exception("Call createShipment() before addPlateToShipment()");
		}
		if(array_key_exists("Dewar", $this->shipmentMessage)){
			throw new \Exception("Shipment contains Dewars, cannot add Plate");
		}
		if(empty($barcode)){ throw new \Exception("Barcode cannot be empty"); }
		if(isset($this->shipmentMessage['Plate'])){
			foreach ($this->shipmentMessage['Plate'] as $existing) {
				if($existing['barcode']===$barcode){
					throw new \Exception("Plate with barcode $barcode already in shipment");
				}
			}
		}
		if($rows<1){ throw new \Exception("Rows must be a positive number"); }
		if($columns<1){ throw new \Exception("Columns must be a positive number"); }
		if($subPositions<1){ throw new \Exception("Sub positions must be a positive number"); }
		if(empty($dropMapping)){
			//Default drop mapping - sub-wells across the top in numerical order, reservoir below
			$part1='';
			$part2='';
			for($i=1;$i<=$subPositions;$i++){
				$part1.=$i;
				$part2.='R';
			}
			$dropMapping=$part1.','.$part2;
		}
		if(!preg_match('/^[\dR,]+$/',$dropMapping)){ throw new \Exception("Mapping is not valid"); }
		$plate=$this->getBaseObject('Plate', $uuid);
		$plate['barcode']=$barcode;
		$plate['containerRef']=['$ref'=>'#/Shipment/Shipment1'];
		$plate['plateType']=[
			'numberRows'=>$rows,
			'numberColumns'=>$columns,
			'numberSubPositions'=>$subPositions,
			'dropMapping'=>$dropMapping
		];
		$this->setObjectToMessage($plate);
		return $plate;
	}

	/**
	 * @see ShipmentEncoderInterface::addWellToPlate()
	 * @throws \Exception
	 */
	public function addWellToPlate(int $plateIndex, int $rowNumber, int $columnNumber, ?string $uuid=null): array {
		$plate=$this->get('Plate',$plateIndex);
		if(!$plate){
			throw new \Exception('No plate with index '.$plateIndex);
		}
		if($rowNumber<1 || $rowNumber>$plate['plateType']['numberRows']){
			throw new \Exception('Row number must be between 1 and '.$plate['plateType']['numberRows']);
		}
		if($columnNumber<1 || $columnNumber>$plate['plateType']['numberColumns']){
			throw new \Exception('Column number must be between 1 and '.$plate['plateType']['numberColumns']);
		}
		if(isset($this->shipmentMessage['PlateWell'])){
			foreach ($this->shipmentMessage['PlateWell'] as $existing){
				if($existing['rowNumber']===$rowNumber && $existing['columnNumber']===$columnNumber && $existing['containerRef']['$ref']==='#/Plate/Plate'.$plateIndex){
					throw new \Exception('Well already exists');
				}
			}
		}
		$well=$this->getBaseObject('PlateWell', $uuid);
		$well['rowNumber']=$rowNumber;
		$well['columnNumber']=$columnNumber;
		$well['containerRef']=['$ref'=>'#/Plate/Plate'.$plateIndex];
		$this->setObjectToMessage($well);
		return $well;
	}

	/**
	 * @see ShipmentEncoderInterface::addDropToPlateWell()
	 * @throws \Exception
	 */
	public function addDropToPlateWell(int $wellIndex, int $dropNumber, int $macromoleculeIndex, ?string $name=null, ?string $uuid=null): array {
		$well=$this->get('PlateWell',$wellIndex);
		$macromolecule=$this->get('Macromolecule',$macromoleculeIndex);
		if(!$well){
			throw new \Exception('No well with index '.$wellIndex);
		}
		if(!$macromolecule){
			throw new \Exception('No macromolecule with index '.$macromoleculeIndex);
		}
		$plateIndex=preg_replace('/\D/', '', $well['containerRef']['$ref']);
		$plate=$this->get('Plate', (int)$plateIndex);
		if(!$plate){
				//Safety, shouldn't be possible
				throw new \Exception('No plate with index '.$plateIndex);
		}
		if($dropNumber<1 || $dropNumber>$plate['plateType']['numberSubPositions']){
			throw new \Exception('Drop number must be between 1 and '.$plate['plateType']['numberSubPositions']);
		}
		if(isset($this->shipmentMessage['WellDrop'])){
			foreach($this->shipmentMessage['WellDrop'] as $existing){
				if($dropNumber==$existing['dropNumber'] && $existing['containerRef']['$ref']==='#/PlateWell/PlateWell'.$wellIndex){
					throw new \Exception('This well drop already exists');
				}
				if($existing['name']===$name){
					throw new \Exception('A well drop with this name already exists');
				}
			}
		}
		if(!$name){
			$name=$plate['barcode'].'_'.$this->plateRowLabels[$well['rowNumber']].str_pad("".$well['columnNumber'], 2, '0',STR_PAD_LEFT).'_'.$dropNumber;
		}
		$sample=$this->getBaseObject('MacromoleculeSample', $uuid);
		$sample['name']=$name;
		$sample['macromoleculeRef']=['$ref'=>'#/Macromolecule/Macromolecule'.$macromoleculeIndex];
		$this->setObjectToMessage($sample);
		$drop=$this->getBaseObject('WellDrop');
		$drop['name']=$name;
		$drop['dropNumber']=$dropNumber;
		$drop['containerRef']=['$ref'=>'#/PlateWell/PlateWell'.$wellIndex];
		$drop['sampleRef']=['$ref'=>'#/MacromoleculeSample/MacromoleculeSample'.$sample['index']];
		$this->setObjectToMessage($drop);
		return [
			'WellDrop'=>$drop,
			'MacromoleculeSample'=>$sample
		];
	}

	/**
	 * @see ShipmentEncoderInterface::getPlateWellByPosition()
	 * @throws \Exception
	 */
	public function getPlateWellByPosition(int $plateIndex, int $rowNumber, int $columnNumber): ?array {
		if(!isset($this->shipmentMessage['Plate']['Plate'.$plateIndex])){
			throw new \Exception('No plate with index '.$plateIndex);
		}
		$foundWell=null;
		if(!isset($this->shipmentMessage['PlateWell'])){ return null; }
		$plateRef='#/Plate/Plate'.$plateIndex;
		foreach ($this->shipmentMessage['PlateWell'] as $well) {
			if ($plateRef === $well['containerRef']['ref'] && $rowNumber === $well['rowNumber'] && $columnNumber === $well['columnNumber']) {
				$foundWell = $well;
				break;
			}
		}
		return $foundWell;
	}

	/**
	 * @see ShipmentEncoderInterface::getWellDropByPosition()
	 * @throws \Exception
	 */
	public function getWellDropByPosition(int $plateIndex, int $rowNumber, int $columnNumber, int $dropNumber): ?array {
		$well=$this->getPlateWellByPosition($plateIndex, $rowNumber, $dropNumber);
		if(!$well){ return null; }
		$foundDrop=null;
		if(!isset($this->shipmentMessage['WellDrop'])) { return null; }
		$wellRef = '#/PlateWell/PlateWell' . $well['index'];
		foreach ($this->shipmentMessage['WellDrop'] as $drop) {
			if ($wellRef === $drop['containerRef']['$ref'] && $dropNumber === $drop['dropNumber']) {
				$foundDrop = $drop;
				break;
			}
		}
		return $foundDrop;
	}


	/**
	 * Adds a drop region.
	 *
	 * For plate regions: Leave $imageMimeType, $imageUrl and $imageData null. Co-ordinate units are assumed to be microns.
	 *
	 * For image regions. Specify $imageMimeType AND ($imageUrl XOR $imageData). Co-ordinate units are assumed to be pixels.
	 *
	 * @param int $dropIndex The index of the drop itself
	 * @param array $region
	 * @param string|null $imageMimeType The image mime-type. Must be present if $imageUrl or $imageData specified.
	 * @param string|null $imageUrl
	 * @param string|null $imageData
	 * @return array
	 * @throws \Exception
	 */
	public function addDropRegion(int $dropIndex, array $region, ?string $imageMimeType=null, ?string $imageUrl=null, ?string $imageData=null): array {
		if(!empty($imageUrl) && !empty($imageData)) {
			throw new \Exception('Cannot specify both imageUrl and imageData; leave both empty for plate coordinates in microns');
		} else if(!empty($imageUrl) || !empty($imageData)){
			if(!empty($imageUrl) && false===filter_var($imageUrl, FILTER_VALIDATE_URL)){
				throw new \Exception('Bad image URL '.$imageUrl);
			}
			if(empty($imageMimeType)){
				throw new \Exception('No image MIME type set');
			} else if(!str_starts_with($imageMimeType, 'image/')){
				throw new \Exception('Bad image MIME type');
			}
		} else if(!empty($imageMimeType)) {
			throw new \Exception('Do not set image MIME type for plate co-ordinates');
		}
		$dropRegion=$this->getBaseObject('DropRegion');
		$dropRegion['containerRef']=['$ref'=>'#/WellDrop/WellDrop'.$dropIndex];
		$dropRegion['region']=[
			'region'=>$region
		];
		if(!empty($imageUrl)){
			$dropRegion['region']['units']='pixel';
			$dropRegion['region']['image']=[
				'mimeType'=>$imageMimeType,
				'image'=>$imageUrl
			];
		} else if(!empty($imageData)){
			$dropRegion['region']['units']='pixel';
			$dropRegion['region']['image']=[
				'mimeType'=>$imageMimeType,
				'data'=>$imageData
			];
		} else {
			//Assumed plate coordinate
			$dropRegion['region']['units']='micron';
		}
		$this->setObjectToMessage($dropRegion);
		return $dropRegion;
	}

	/**
	 * @see ShipmentEncoderInterface::addPointDropRegionByPlateDropIndex()
	 * @throws \Exception
	 */
	public function addPointDropRegionByPlateDropIndex(int $dropIndex, int $x, int $y, ?string $imageMimeType=null, ?string $imageUrl=null, ?string $imageData=null): array {
		if($x<0 || $y<0){ throw new \Exception('x and y cannot be negative'); }
		$point=[
			'regionType'=>'point',
			'x'=>$x,
			'y'=>$y
		];
		return $this->addDropRegion($dropIndex, $point, $imageMimeType, $imageUrl, $imageData);
	}

	/**
	 * @see ShipmentEncoderInterface::addCrystalToDropRegion()
	 * @throws \Exception
	 */
	public function addCrystalToDropRegion(int $dropRegionIndex, string $name, ?string $uuid=null): array {
		$dropRegion=$this->get('DropRegion', $dropRegionIndex);
		if(!$dropRegion){ throw new \Exception('No DropRegion with index '.$dropRegionIndex); }
		$crystal=$this->getBaseObject('Crystal', $uuid);
		$crystal['name']=$name;
		$wellDrop=$this->getByJsonPath($dropRegion['containerRef']);
		$crystal['sampleRef']=$wellDrop['sampleRef'];
		$crystal['containerRef']=['$ref'=>'#/DropRegion/DropRegion'.$dropRegion['index']];
		$this->setObjectToMessage($crystal);
		return $crystal;
	}


	/**
	 * Checks that all parent objects are referred to by a child (for example, that all Dewars contain at least one Puck).
	 * Assumes that only one key in the child object will refer to the parent.
	 * @param string $parentType The parent type.
	 * @param string $childType The child type.
	 * @return void if all parents are referred to by at least one child.
	 * @throws \Exception if none of the parent type are present.
	 * @throws \Exception if none of the child type are present.
	 * @throws \Exception if any parent is not referred to by at least one child.
	 */
	public function validateAllParentsHaveChild(string $parentType, string $childType): void {
		if(!isset($this->shipmentMessage[$parentType])){ throw new \Exception("No {$parentType}s in the shipment"); }
		if(!isset($this->shipmentMessage[$childType])){ throw new \Exception("No {$childType}s in the shipment"); }
		if(!isset($this->shipmentMessage[$childType][$childType.'1'])){ throw new \Exception("No {$childType}1 in the shipment"); }
		$parentKeys=[];
		$referenceKey='';
		foreach ($this->shipmentMessage[$childType][$childType.'1'] as $k=>$v) {
			if(isset($v['$ref'])){
				$parts=explode('/', $v['$ref']);
				if($parts[1]===$parentType) {
					$referenceKey = $k;
					break;
				}
			}
		}
		if(''===$referenceKey) { throw new \Exception("Cannot determine child property that refers to $parentType in $childType"); }

		foreach ($this->shipmentMessage[$childType] as $child) {
			$parentKey=(explode('/', $child[$referenceKey]['$ref']))[2]; // "#/Dewar/Dewar1"
			$parentKeys[]=$parentKey;
		}
		$parentKeys=array_unique($parentKeys);
		foreach(array_keys($this->shipmentMessage[$parentType]) as $toCheck){
			if(!in_array($toCheck, $parentKeys)){
				throw new \Exception("$toCheck is not referred to by any $childType");
			}
			if(count($parentKeys)!==count($this->shipmentMessage[$parentType])){
				throw new \Exception("Count mismatch - number of {$parentType}s does not match number of {$parentType}s referred to by {$childType}s");
			}
		}
	}

	/**
	 * @see ShipmentEncoderInterface::validate()
	 * @throws \Exception
	 */
	public function validate(): bool {
		$shipment=$this->get('Shipment',1);
		$dewar1=$this->get('Dewar',1);
		$plate1=$this->get('Plate',1);
		$macromolecule1=$this->get('Macromolecule',1);
		if(!$shipment){ throw new \Exception("No shipment"); }
		if(!isset($shipment['labContactOutbound'])){ throw new \Exception("No outbound lab contact"); }
		if(!isset($shipment['labContactReturn'])){ throw new \Exception("No return lab contact"); }
		if(!$dewar1 && !$plate1){ throw new \Exception("No Dewars or Plates in the shipment"); }
		if(!$macromolecule1){ throw new \Exception("No Macromolecules in the shipment"); }

		if($dewar1){
			$this->validateAllParentsHaveChild('Dewar','Puck');
			$this->validateAllParentsHaveChild('Shipment','Dewar');
			if(isset($this->shipmentMessage['Pin'])){
				$this->validateAllParentsHaveChild('Puck','Pin');
				$this->validateAllParentsHaveChild('MacromoleculeSample','Pin');
				$this->validateAllParentsHaveChild('Macromolecule','MacromoleculeSample');
			} else if(isset($this->shipmentMessage['MultiPin'])){
				$this->validateAllParentsHaveChild('Puck','MultiPin');
				$this->validateAllParentsHaveChild('MultiPin','PinPosition');
				$this->validateAllParentsHaveChild('MacromoleculeSample','PinPosition');
			} else {
				throw new \Exception("No Pins or MultiPins in the shipment");
			}
		} else {
			$this->validateAllParentsHaveChild('Plate','PlateWell');
			$this->validateAllParentsHaveChild('PlateWell','WellDrop');
			$this->validateAllParentsHaveChild('WellDrop','DropRegion');

		}

		if(isset($this->shipmentMessage['Dewar'])){
			if(isset($this->shipmentMessage['Pin'])){
				if(!isset($this->shipmentMessage['MacromoleculeSample'])){
					throw new \Exception("No samples in the shipment");
				}
			} else if(isset($this->shipmentMessage['MultiPin'])){
				if(!isset($this->shipmentMessage['MacromoleculeSample'])){
					throw new \Exception("No samples in the shipment");
				}
			} else {
				throw new \Exception("No pins in the shipment");
			}
		} else if(isset($this->shipmentMessage['Plate'])){
			if(!isset($this->shipmentMessage['Crystal'])){
				throw new \Exception("No crystal in the shipment");
			}
		}
		return true;
	}

	/**
	 * @see ShipmentEncoderInterface::validate()
	 * @throws \Exception
	 */
	public function encodeToJSON(bool $prettyPrint=false): string {
		$this->validate();
		$flags=null;
		if($prettyPrint){
			$flags=JSON_PRETTY_PRINT;
		}
		return json_encode($this->shipmentMessage, $flags);
	}

}

