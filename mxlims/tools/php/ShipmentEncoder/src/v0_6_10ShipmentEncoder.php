<?php

namespace mxlims\tools\php\ShipmentEncoder\src;

include_once __DIR__.'/ShipmentEncoderInterface.php';
include_once __DIR__.'/v0_6_7ShipmentEncoder.php';

class v0_6_10ShipmentEncoder extends v0_6_7ShipmentEncoder {

	public function createShipment(string $proposalCode, ?int $sessionNumber=null, ?string $uuid=null): array {
		if(!empty($this->shipmentMessage)){
			throw new \Exception("Shipment already added to message");
		}
		if(!preg_match('/^[0-9A-Za-z]+$/', $proposalCode)){
			throw new \Exception("Bad proposal code $proposalCode");
		}
		$shipment=$this->getBaseObject('Shipment', $uuid);
		$shipment['proposalCode']=$proposalCode;
		if(!empty($sessionNumber)){
			if($sessionNumber<1){
				throw new \Exception("Session number must be a positive number");
			}
			$shipment['sessionNumber'] = $sessionNumber;
		}
		$this->shipmentMessage=[
			'version'=>$this->getVersion()
		];
		$this->setObjectToMessage($shipment);
		return $shipment;
	}

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
			'uuid' => $uuid
		];
	}

	/**
	 * @param array $mxlimsObject The MXLIMS object.
	 * @param string $domainName Uniquely identifies the site where this URL is relevant. The whole subdomain.domain.tld need not resolve, but the domain.tld part should resolve.
	 * @param string|int $identifier Am identifier pointing to this object in some LIMS related to (but not necessarily at) $domainName.
	 * @param string $url A URL pointing to this object in some LIMS related to (but not necessarily at) $domainName.
	 * @return array
	 * @throws \Exception
	 */
	public function addIdentifierAndUrlToObject(array $mxlimsObject, string $domainName, string|int $identifier, string $url): array {
		$this->addIdentifierOrUrlToObject($mxlimsObject, $domainName, $identifier, 'identifier');
		return $this->addIdentifierOrUrlToObject($mxlimsObject, $domainName, $url, 'url');
	}

	/**
	 * @param array $mxlimsObject The MXLIMS object.
	 * @param string $domainName Uniquely identifies the site where this URL is relevant. The whole subdomain.domain.tld need not resolve, but the domain.tld part should resolve.
	 * @param string|int $identifier Am identifier pointing to this object in some LIMS related to (but not necessarily at) $domainName.
	 * @throws \Exception
	 */
	public function addIdentifierToObject(array $mxlimsObject, string $domainName, string|int $identifier): array {
		return $this->addIdentifierOrUrlToObject($mxlimsObject, $domainName, $identifier, 'identifier');
	}

	/**
	 * @param array $mxlimsObject The MXLIMS object.
	 * @param string $domainName Uniquely identifies the site where this URL is relevant. The whole subdomain.domain.tld need not resolve, but the domain.tld part should resolve.
	 * @param string $url A URL pointing to this object in some LIMS related to (but not necessarily at) $domainName.
	 * @return array
	 * @throws \Exception
	 */
	public function addUrlToObject(array $mxlimsObject, string $domainName, string $url): array {
		return $this->addIdentifierOrUrlToObject($mxlimsObject, $domainName, $url, 'url');
	}

	/**
	 * @throws \Exception
	 */
	private function addIdentifierOrUrlToObject(array $mxlimsObject, string $domainName, string|int $identifierOrUrl, string $which): array {
		if(!isset($mxlimsObject['mxlimsType'])){ throw new \Exception('No mxlimsType key on object, cannot determine type'); }
		if(!isset($mxlimsObject['index'])){ throw new \Exception('No index key on object, cannot determine index'); }
		$mxlimsType=$mxlimsObject['mxlimsType'];
		$index=$mxlimsObject['index'];
		$acceptableTypes=['identifier','url'];
		if(!in_array($which, $acceptableTypes)){
			throw new \Exception('Unacceptable type, must be one of ['.implode(',', $acceptableTypes).']');
		}
		if(!preg_match('/^(?i)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$/', $domainName)){
			throw new \Exception("Bad domain name $domainName");
		}
		$object=$this->get($mxlimsType, $index);
		if(!$object){ throw new \Exception("No $mxlimsType with index $index"); }
		$which=$which.'s';
		if(!isset($object[$which])){
			$object[$which]=[];
		}
		$object[$which][$domainName]=$identifierOrUrl;
		$this->setObjectToMessage($object);
		return $object;
	}

}

