# Serol
Serol's Cosmic Explorer website

## An astronomy exploration website for LCO education partners

At present Serol is only available for [LCO education partners](https://lco.global/education/partners/).

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
