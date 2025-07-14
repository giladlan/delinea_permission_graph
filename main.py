from jsonlines import open as json_lines_reader

from permission_graph.permission_graph import PermissionGraph

if __name__ == '__main__':
    permission_graph = PermissionGraph()

    with json_lines_reader('.\permissions_file') as permissions:
        permission_graph.build_from_parsed_permissions(list(permissions))

    folder_93198982071_hierarchy = permission_graph.get_hierarchy_for_resource('folders/93198982071')
    assert folder_93198982071_hierarchy == ['folders/96505015065',
                                            'folders/767216091627',
                                            'organizations/1066060271767']

    permissions_for_devops_dude = permission_graph.get_permissions_for_identity(
        'devops-dude-1@striking-arbor-264209.iam.gserviceaccount.com')
    assert permissions_for_devops_dude == [('folders/188906894377', 'folder', 'roles/owner')]
