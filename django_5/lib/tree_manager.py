from typing import Union, Optional

from django.core.cache import cache
from django.db import models


class TreeManager(models.Manager):
    __paths: dict[int, list[int]] = {}

    def get(self) -> dict[str, Union[dict[int, list[int]], dict[int, dict]]]:

        res = cache.get('sections_tree_manager_result_cache')
        if not res:
            res = {
                'tree': self.__sort(self.__build()),
                'paths': self.__paths,
            }
            cache.set('sections_tree_manager_result_cache', res, 3600 * 24 * 365 * 888)
        return res

    def get_el(self, el_id: int) -> 'Sections':

        res = self.get()
        if res['paths'].get(el_id) is None:
            return res['tree'][el_id]
        return eval(
            f'res["tree"][{
            ']["children"]['.join(map(str, res['paths'][el_id]))
            }]["children"][{el_id}]'
        )

    def __sort(self, tree: dict[int, dict[str, dict]]) -> dict[int, dict[str, dict]]:

        for_sort: dict = {}
        for res_key in list(tree):
            for_sort[res_key] = tree[res_key]['el'].sort
            if 'children' in tree[res_key]:
                tree[res_key]['children'] = self.__sort(tree[res_key]['children'])
        sort_res = dict(sorted(for_sort.items(), key=lambda item: item[1]))
        res_sorted = {}
        for sort_res_key in list(sort_res):
            res_sorted[sort_res_key] = tree[sort_res_key]
        return res_sorted

    def __build(
            self,
            el_id: Optional[int] = None,
            els: Optional[dict[int, dict[str, Optional[Union[int, str]]]]] = None,
            path: Optional[list[int]] = None,
    ) -> dict[int, dict[str, dict]]:

        res = {}
        if el_id is None:
            els = {}
            for item in super().get_queryset():
                els[item.pk] = item
        for item_k in list(els):
            if els.get(item_k) is None:
                continue
            item_v = els[item_k]
            if item_v.parent_id == el_id:
                if path is None:
                    cat_path = [el_id]
                else:
                    cat_path = path.copy()
                    cat_path.append(el_id)
                if cat_path == [None]:
                    cat_path = []
                else:
                    self.__paths[item_k] = cat_path
                res[item_k] = {'el': item_v}
                del els[item_k]
                res[item_k]['children'] = self.__build(item_k, els, cat_path)
                if not res[item_k]['children']:
                    del res[item_k]['children']
        return res
