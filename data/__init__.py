# Python imports
import json

# Own imports
from logica_api.models.branch import BranchModel
from logica_api.models.client import ClientModel
from logica_api.models.product import ProductModel
from logica_api.schemas.branch import BranchSchema
from logica_api.schemas.client import ClientSchema
from logica_api.schemas.product import ProductSchema


class InitialData:
    """
    Clase para cargar datos iniciales en la base de datos.
    """

    async def upload_branch_async(self):
        """
        Carga las sucursales en la base de datos.
        """
        try:
            count = await BranchModel.get_count_async()
            if count > 0:
                raise Exception("Ya existen registros en la base de datos.")
            with open("data/branch.json", encoding="utf-8") as file:
                branch = json.load(file)
        except Exception as e:
            print(
                f"El archivo branch.json no existe, está dañado o la base de datos ya contiene registros: {e}"
            )
        else:
            for item in branch:
                schema = BranchSchema(
                    gln_sucursal=item["GLN_Sucursal"], name=item["Name"]
                )
                await BranchModel.create_async(schema)

    async def upload_client_async(self):
        """
        Carga los clientes en la base de datos.
        """
        try:
            count = await ClientModel.get_count_async()
            if count > 0:
                raise Exception("Ya existen registros en la base de datos.")
            with open(
                "data/client.json",
                encoding="utf-8",
            ) as file:
                client = json.load(file)
        except Exception as e:
            print(
                f"El archivo client.json no existe, está dañado o la base de datos ya contiene registros: {e}"
            )
        else:
            for item in client:
                schema = ClientSchema(
                    gln_cliente=item["GLN_Cliente"],
                    names=item["Names"],
                    age=item["Age"],
                    phone=item["Phone"],
                    email=item["Email"],
                )
                await ClientModel.create_async(schema)

    async def upload_product_async(self):
        """
        Carga los productos en la base de datos.
        """
        try:
            count = await ProductModel.get_count_async()
            if count > 0:
                raise Exception("Ya existen registros en la base de datos.")
            with open("data/product.json", encoding="utf-8") as file:
                product = json.load(file)
        except Exception as e:
            print(
                f"El archivo product.json no existe, está dañado o la base de datos ya contiene registros: {e}"
            )
        else:
            for item in product:
                schema = ProductSchema(
                    gtin_producto=item["Gtin_Producto"],
                    name=item["Name"],
                    description=item["Description"],
                )
                await ProductModel.create_async(schema)

    async def upload_data_async(self):
        """
        Carga los datos iniciales en la base de datos.
        """
        tasks = (
            self.upload_branch_async(),
            self.upload_client_async(),
            self.upload_product_async(),
        )
        for task in tasks:
            await task
