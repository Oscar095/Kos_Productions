import pandas as pd
import requests

headers = {
"ConniKey" : "2151a36b5f98858457784a4d3eb88788",
"ConniToken" : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6Ijk5MjIxZDE1LTkwZjItNDVjNi1iZDc5LTczMGIxNTVkMDA1NiIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcHJpbWFyeXNpZCI6IjhkOTEyMDEwLTFkMGEtNDE1MS1hNmEyLTA2NmFjNzM4ODMyYSJ9.7epvbp5HCSlwTNJvRtFXCi1ToxeK9oQXnm2Bg-gGAQw"
 }
response = requests.get("https://servicios.siesacloud.com/api/connekta/v3/ejecutarconsulta?idCompania=7501&descripcion=koscolombia_op_numeros&paginacion=numPag=1|tamPag=100" \
"", headers=headers)

data=response.json()
datos=pd.DataFrame(data["detalle"]["Datos"])


print(datos)