tracker_response = """<s:Envelope xmlns:a="http://www.w3.org/2005/08/addressing" xmlns:r="http://schemas.xmlsoap.org/ws/2005/02/rm" xmlns:s="http://www.w3.org/2003/05/soap-envelope">
	<s:Header>
		<r:Sequence s:mustUnderstand="1">
			<r:Identifier>urn:uuid:2b7b79bb-6c8e-476b-a5a7-c99988bdaef0</r:Identifier>
			<r:MessageNumber>2</r:MessageNumber>
		</r:Sequence>
		<r:SequenceAcknowledgement>
			<r:Identifier>urn:uuid:5258cc40-009c-41ca-89fa-530739676df8</r:Identifier>
			<r:AcknowledgementRange Lower="1" Upper="2"/>
			<netrm:BufferRemaining xmlns:netrm="http://schemas.microsoft.com/ws/2006/05/rm">8</netrm:BufferRemaining>
		</r:SequenceAcknowledgement>
		<a:Action s:mustUnderstand="1">http://tempuri.org/IBasic/Trackers_GetAllTrackersResponse</a:Action>
		<a:RelatesTo>urn:uuid:8091adc5-0c6b-4806-bbc8-b71fe56db249</a:RelatesTo>
	</s:Header>
	<s:Body>
		<Trackers_GetAllTrackersResponse xmlns="http://tempuri.org/">
			<Trackers_GetAllTrackersResult xmlns:b="http://schemas.datacontract.org/2004/07/PublicSoapApi.DTO.Model" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
				<b:DTTracker>
					<b:ContractNo i:nil="true"/>
					<b:CreatedAt i:nil="true"/>
					<b:Description>BS84272</b:Description>
					<b:Gsm/>
					<b:ID>15789</b:ID>
					<b:IMEI>68165</b:IMEI>
					<b:InsurranceFor i:nil="true"/>
					<b:IsAvailable>false</b:IsAvailable>
					<b:IsConnectedToVD>false</b:IsConnectedToVD>
					<b:Marker>H122</b:Marker>
					<b:Position i:nil="true"/>
					<b:Subscription>NONE</b:Subscription>
					<b:UserID>6851</b:UserID>
				</b:DTTracker>
				<b:DTTracker>
					<b:ContractNo i:nil="true"/>
					<b:CreatedAt i:nil="true"/>
					<b:Description>BS84273</b:Description>
					<b:Gsm>93725246</b:Gsm>
					<b:ID>15794</b:ID>
					<b:IMEI>98498</b:IMEI>
					<b:InsurranceForm i:nil="true"/>
					<b:IsAvailable>false</b:IsAvailable>
					<b:IsConnectedToVD>false</b:IsConnectedToVD>
					<b:Marker>H123</b:Marker>
					<b:Position i:nil="true"/>
					<b:Subscription>NONE</b:Subscription>
					<b:UserID>6841</b:UserID>
				</b:DTTracker>
				<b:DTTracker>
					<b:ContractNo i:nil="true"/>
					<b:CreatedAt i:nil="true"/>
					<b:Description>BS84255</b:Description>
					<b:Gsm>93725123</b:Gsm>
					<b:ID>15812</b:ID>
					<b:IMEI>65198</b:IMEI>
					<b:InsurranceForm i:nil="true"/>
					<b:IsAvailable>false</b:IsAvailable>
					<b:IsConnectedToVD>false</b:IsConnectedToVD>
					<b:Marker>H120</b:Marker>
					<b:Position i:nil="true"/>
					<b:Subscription>NONE</b:Subscription>
					<b:UserID>96849</b:UserID>
				</b:DTTracker>
				<b:DTTracker>
					<b:ContractNo i:nil="true"/>
					<b:CreatedAt i:nil="true"/>
					<b:Description>BL80494</b:Description>
					<b:Gsm>93725051</b:Gsm>
					<b:ID>15873</b:ID>
					<b:IMEI>6948984</b:IMEI>
					<b:InsurranceForm i:nil="true"/>
					<b:IsAvailable>false</b:IsAvailable>
					<b:IsConnectedToVD>false</b:IsConnectedToVD>
					<b:Marker>90</b:Marker>
					<b:Position i:nil="true"/>
					<b:Subscription>NONE</b:Subscription>
					<b:UserID>98468</b:UserID>
				</b:DTTracker>
			</Trackers_GetAllTrackersResult>
		</Trackers_GetAllTrackersResponse>
	</s:Body>
</s:Envelope>"""



mileage_response = """
<s:Envelope xmlns:a="http://www.w3.org/2005/08/addressing" xmlns:r="http://schemas.xmlsoap.org/ws/2005/02/rm" xmlns:s="http://www.w3.org/2003/05/soap-envelope">
	<s:Header>
		<r:Sequence s:mustUnderstand="1">
			<r:Identifier>urn:uuid:d3f1c3a4-4055-4404-8b11-cb0cb1b07e67</r:Identifier>
			<r:MessageNumber>2</r:MessageNumber>
		</r:Sequence>
		<r:SequenceAcknowledgement>
			<r:Identifier>urn:uuid:20d55597-afd8-450d-bd62-1cce183c7c73</r:Identifier>
			<r:AcknowledgementRange Lower="1" Upper="2"/>
			<netrm:BufferRemaining xmlns:netrm="http://schemas.microsoft.com/ws/2006/05/rm">8</netrm:BufferRemaining>
		</r:SequenceAcknowledgement>
		<a:Action s:mustUnderstand="1">http://tempuri.org/IBasic/Trackers_GetMilageLogResponse</a:Action>
		<a:RelatesTo>urn:uuid:27cfe5ec-ed4a-493b-83ea-854e1f4764a4</a:RelatesTo>
	</s:Header>
	<s:Body>
		<Trackers_GetMilageLogResponse xmlns="http://tempuri.org/">
			<Trackers_GetMilageLogResult xmlns:b="http://schemas.datacontract.org/2004/07/PublicSoapApi.DTO.Model" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
				<b:DTMileageLog>
					<b:Comment/>
					<b:ID>109165318</b:ID>
					<b:IsAproved>false</b:IsAproved>
					<b:IsEdited>true</b:IsEdited>
					<b:IsPrivate>false</b:IsPrivate>
					<b:Meters>22</b:Meters>
					<b:StartPos>
						<b:BatteryPercent i:nil="true"/>
						<b:BatteryVoltage i:nil="true"/>
						<b:City>John</b:City>
						<b:Country>DK</b:Country>
						<b:ExternalVoltage i:nil="true"/>
						<b:Lat i:nil="true"/>
						<b:Lon i:nil="true"/>
						<b:Sat i:nil="true"/>
						<b:Speed i:nil="true"/>
						<b:Street>Johnvej</b:Street>
						<b:Timestamp>2023-08-14T13:39:05</b:Timestamp>
						<b:Zipcode>8260</b:Zipcode>
						<b:sLat>56</b:sLat>
						<b:sLon>10</b:sLon>
					</b:StartPos>
					<b:StopPos>
						<b:BatteryPercent i:nil="true"/>
						<b:BatteryVoltage i:nil="true"/>
						<b:City>John</b:City>
						<b:Country>DK</b:Country>
						<b:ExternalVoltage i:nil="true"/>
						<b:Lat i:nil="true"/>
						<b:Lon i:nil="true"/>
						<b:Sat i:nil="true"/>
						<b:Speed i:nil="true"/>
						<b:Street>Johnvej</b:Street>
						<b:Timestamp>2023-08-14T13:39:16</b:Timestamp>
						<b:Zipcode>8260</b:Zipcode>
						<b:sLat>56</b:sLat>
						<b:sLon>10</b:sLon>
					</b:StopPos>
				</b:DTMileageLog>
				<b:DTMileageLog>
					<b:Comment/>
					<b:ID>109165319</b:ID>
					<b:IsAproved>false</b:IsAproved>
					<b:IsEdited>true</b:IsEdited>
					<b:IsPrivate>false</b:IsPrivate>
					<b:Meters>1445</b:Meters>
					<b:StartPos>
						<b:BatteryPercent i:nil="true"/>
						<b:BatteryVoltage i:nil="true"/>
						<b:City>John</b:City>
						<b:Country>DK</b:Country>
						<b:ExternalVoltage i:nil="true"/>
						<b:Lat i:nil="true"/>
						<b:Lon i:nil="true"/>
						<b:Sat i:nil="true"/>
						<b:Speed i:nil="true"/>
						<b:Street>Johnvej</b:Street>
						<b:Timestamp>2023-08-14T13:41:11</b:Timestamp>
						<b:Zipcode>8260</b:Zipcode>
						<b:sLat>56</b:sLat>
						<b:sLon>10</b:sLon>
					</b:StartPos>
					<b:StopPos>
						<b:BatteryPercent i:nil="true"/>
						<b:BatteryVoltage i:nil="true"/>
						<b:City>John</b:City>
						<b:Country>DK</b:Country>
						<b:ExternalVoltage i:nil="true"/>
						<b:Lat i:nil="true"/>
						<b:Lon i:nil="true"/>
						<b:Sat i:nil="true"/>
						<b:Speed i:nil="true"/>
						<b:Street>Johnvej</b:Street>
						<b:Timestamp>2023-08-14T13:45:52</b:Timestamp>
						<b:Zipcode>8260</b:Zipcode>
						<b:sLat>56</b:sLat>
						<b:sLon>10</b:sLon>
					</b:StopPos>
				</b:DTMileageLog>
				<b:DTMileageLog>
					<b:Comment/>
					<b:ID>109165320</b:ID>
					<b:IsAproved>false</b:IsAproved>
					<b:IsEdited>true</b:IsEdited>
					<b:IsPrivate>false</b:IsPrivate>
					<b:Meters>261</b:Meters>
					<b:StartPos>
						<b:BatteryPercent i:nil="true"/>
						<b:BatteryVoltage i:nil="true"/>
						<b:City>John</b:City>
						<b:Country>DK</b:Country>
						<b:ExternalVoltage i:nil="true"/>
						<b:Lat i:nil="true"/>
						<b:Lon i:nil="true"/>
						<b:Sat i:nil="true"/>
						<b:Speed i:nil="true"/>
						<b:Street>Johnvej</b:Street>
						<b:Timestamp>2023-08-14T14:02:49</b:Timestamp>
						<b:Zipcode>8260</b:Zipcode>
						<b:sLat>56</b:sLat>
						<b:sLon>10</b:sLon>
					</b:StartPos>
					<b:StopPos>
						<b:BatteryPercent i:nil="true"/>
						<b:BatteryVoltage i:nil="true"/>
						<b:City>John</b:City>
						<b:Country>DK</b:Country>
						<b:ExternalVoltage i:nil="true"/>
						<b:Lat i:nil="true"/>
						<b:Lon i:nil="true"/>
						<b:Sat i:nil="true"/>
						<b:Speed i:nil="true"/>
						<b:Street>Johnvej</b:Street>
						<b:Timestamp>2023-08-14T14:04:53</b:Timestamp>
						<b:Zipcode>8260</b:Zipcode>
						<b:sLat>56</b:sLat>
						<b:sLon>10</b:sLon>
					</b:StopPos>
				</b:DTMileageLog>
				<b:DTMileageLog>
					<b:Comment/>
					<b:ID>109165321</b:ID>
					<b:IsAproved>false</b:IsAproved>
					<b:IsEdited>true</b:IsEdited>
					<b:IsPrivate>false</b:IsPrivate>
					<b:Meters>309</b:Meters>
					<b:StartPos>
						<b:BatteryPercent i:nil="true"/>
						<b:BatteryVoltage i:nil="true"/>
						<b:City>John</b:City>
						<b:Country>DK</b:Country>
						<b:ExternalVoltage i:nil="true"/>
						<b:Lat i:nil="true"/>
						<b:Lon i:nil="true"/>
						<b:Sat i:nil="true"/>
						<b:Speed i:nil="true"/>
						<b:Street>Johnvej</b:Street>
						<b:Timestamp>2023-08-14T14:08:02</b:Timestamp>
						<b:Zipcode>8260</b:Zipcode>
						<b:sLat>56</b:sLat>
						<b:sLon>10</b:sLon>
					</b:StartPos>
					<b:StopPos>
						<b:BatteryPercent i:nil="true"/>
						<b:BatteryVoltage i:nil="true"/>
						<b:City>John</b:City>
						<b:Country>DK</b:Country>
						<b:ExternalVoltage i:nil="true"/>
						<b:Lat i:nil="true"/>
						<b:Lon i:nil="true"/>
						<b:Sat i:nil="true"/>
						<b:Speed i:nil="true"/>
						<b:Street>Johnvej</b:Street>
						<b:Timestamp>2023-08-14T14:08:56</b:Timestamp>
						<b:Zipcode>8260</b:Zipcode>
						<b:sLat>56</b:sLat>
						<b:sLon>10</b:sLon>
					</b:StopPos>
				</b:DTMileageLog>
				<b:DTMileageLog>
					<b:Comment/>
					<b:ID>109169995</b:ID>
					<b:IsAproved>false</b:IsAproved>
					<b:IsEdited>true</b:IsEdited>
					<b:IsPrivate>false</b:IsPrivate>
					<b:Meters>216</b:Meters>
					<b:StartPos>
						<b:BatteryPercent i:nil="true"/>
						<b:BatteryVoltage i:nil="true"/>
						<b:City>John</b:City>
						<b:Country>DK</b:Country>
						<b:ExternalVoltage i:nil="true"/>
						<b:Lat i:nil="true"/>
						<b:Lon i:nil="true"/>
						<b:Sat i:nil="true"/>
						<b:Speed i:nil="true"/>
						<b:Street>Johnvej</b:Street>
						<b:Timestamp>2023-08-14T15:08:14</b:Timestamp>
						<b:Zipcode>8270</b:Zipcode>
						<b:sLat>56</b:sLat>
						<b:sLon>10</b:sLon>
					</b:StartPos>
					<b:StopPos>
						<b:BatteryPercent i:nil="true"/>
						<b:BatteryVoltage i:nil="true"/>
						<b:City>John</b:City>
						<b:Country>DK</b:Country>
						<b:ExternalVoltage i:nil="true"/>
						<b:Lat i:nil="true"/>
						<b:Lon i:nil="true"/>
						<b:Sat i:nil="true"/>
						<b:Speed i:nil="true"/>
						<b:Street>Johnvej</b:Street>
						<b:Timestamp>2023-08-14T15:09:54</b:Timestamp>
						<b:Zipcode>8270</b:Zipcode>
						<b:sLat>56</b:sLat>
						<b:sLon>10</b:sLon>
					</b:StopPos>
				</b:DTMileageLog>
				<b:DTMileageLog>
					<b:Comment/>
					<b:ID>109169996</b:ID>
					<b:IsAproved>false</b:IsAproved>
					<b:IsEdited>true</b:IsEdited>
					<b:IsPrivate>false</b:IsPrivate>
					<b:Meters>1417</b:Meters>
					<b:StartPos>
						<b:BatteryPercent i:nil="true"/>
						<b:BatteryVoltage i:nil="true"/>
						<b:City>John</b:City>
						<b:Country>DK</b:Country>
						<b:ExternalVoltage i:nil="true"/>
						<b:Lat i:nil="true"/>
						<b:Lon i:nil="true"/>
						<b:Sat i:nil="true"/>
						<b:Speed i:nil="true"/>
						<b:Street>Johnvej</b:Street>
						<b:Timestamp>2023-08-14T15:22:02</b:Timestamp>
						<b:Zipcode>8270</b:Zipcode>
						<b:sLat>56</b:sLat>
						<b:sLon>10</b:sLon>
					</b:StartPos>
					<b:StopPos>
						<b:BatteryPercent i:nil="true"/>
						<b:BatteryVoltage i:nil="true"/>
						<b:City>John</b:City>
						<b:Country>DK</b:Country>
						<b:ExternalVoltage i:nil="true"/>
						<b:Lat i:nil="true"/>
						<b:Lon i:nil="true"/>
						<b:Sat i:nil="true"/>
						<b:Speed i:nil="true"/>
						<b:Street>Johnvej</b:Street>
						<b:Timestamp>2023-08-14T15:24:03</b:Timestamp>
						<b:Zipcode>8260</b:Zipcode>
						<b:sLat>56</b:sLat>
						<b:sLon>10</b:sLon>
					</b:StopPos>
				</b:DTMileageLog>
			</Trackers_GetMilageLogResult>
		</Trackers_GetMilageLogResponse>
	</s:Body>
</s:Envelope>
"""
