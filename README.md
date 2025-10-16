# Serol
Serol's Cosmic Explorer website

## APIs used

Serol uses the following LCO maintained APIs
- RTI bridge ephemeris to get an up to date list of planets visible
- Simbad 2 K for planet orbital elements
- WhatsUp for sidereal target list

## Necessary set up
- For people without an LCO account to use Serol, there is a service account user "serol"
- These people's requests are attached to proposal LCOEPO2014B-010. This proposal needs time put into it every semester for 0m4 observing.

### Get snapshot of live site:

```
kubectl exec -it <pod-name> -n prod -c backend -- python manage.py dumpdata  -e sessions -e admin --natural-foreign --natural-primary | gzip > fullsite.json.gz
```

Read data into local sandbox with:
```
./manage.py migrate; ./manage.py loaddata fullsite.json.gz

## License

This project is licensed under the MIT License. Please see the
[LICENSE](LICENSE) file for details. 

## Authors

This project is maintained by the [Las Cumbres Observatory](https://lco.global/)
staff.
