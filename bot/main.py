from typing import Optional
from ares.consts import UnitRole
from ares import AresBot
from ares.behaviors.combat import CombatManeuver
from cython_extensions import cy_closest_to, cy_distance_to
from ares.behaviors.combat.individual import (
    AMove,
    PathUnitToTarget,
    StutterUnitBack,
    AttackTarget,
    KeepUnitSafe,
)
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2

import time # for debug tool

import numpy as np


class MyBot(AresBot):

    combat_manager = None
    ZERG_UNIT_TYPE: set[UnitTypeId] = { UnitTypeId.ZERGLING, UnitTypeId.ROACH }

    last_debug_time = 0 # Debug tool
    


    def __init__(self, game_step_override: Optional[int] = None):
        """Initiate custom bot

        Parameters
        ----------
        game_step_override :
            If provided, set the game_step to this value regardless of how it was
            specified elsewhere
        """
        super().__init__(game_step_override)




    async def on_start(self):
        
        await super().on_start()
        print("Game started")
        self.chat_send("teste 123")



#_______________________________________________________________________________________________________________________
#          ON STEP
#_______________________________________________________________________________________________________________________



    async def on_step(self, iteration: int) -> None:
        await super(MyBot, self).on_step(iteration)

        # define targets and grid
        enemy_units = self.enemy_units
        ground_grid = self.mediator.get_ground_grid
        attack_target = None

        self.zergling_squad = Units = self.mediator.get_units_from_role(role=UnitRole.CONTROL_GROUP_ONE)
        roach_squad = Units = self.mediator.get_units_from_role(role=UnitRole.CONTROL_GROUP_TWO)
        queen_squad = Units = self.mediator.get_units_from_role(role=UnitRole.CONTROL_GROUP_THREE)
        drone_squad = Units = self.mediator.get_units_from_role(role=UnitRole.CONTROL_GROUP_FOUR)
        baneling_squad = Units = self.mediator.get_units_from_role(role=UnitRole.CONTROL_GROUP_FIVE)



        await self.debug_tool()

        if enemy_units:
            target = enemy_units[0].position
        else:
            target = self.game_info.map_center


        if self.zergling_squad:
            self.zergling_army_attack(self.zergling_squad, target, ground_grid)    

        #for unit in self.units(UnitTypeId.ZERGLING):
            #unit(AMove(unit=unit, target=target))
            #unit.attack(target)
        #    self.register_behavior(AMove(unit, target))


        for unit in self.units(UnitTypeId.ROACH):
            #unit(AMove(unit=unit, target=target))
            #unit.attack(target)
            self.register_behavior(AMove(unit, target))

        for unit in self.units(UnitTypeId.QUEEN):
            #unit(AMove(unit=unit, target=target))
            #unit.attack(target)
            self.register_behavior(AMove(unit, target))


        for unit in self.units(UnitTypeId.DRONE):
            #unit(AMove(unit=unit, target=target))
            #unit.attack(target)
            self.register_behavior(AMove(unit, target))



        for unit in self.units(UnitTypeId.BANELING):
            #unit(AMove(unit=unit, target=target))
            #unit.attack(target)
            self.register_behavior(AMove(unit, target))

        for unit in self.units(UnitTypeId.RAVAGER):
            #unit(AMove(unit=unit, target=target))
            #unit.attack(target)
            self.register_behavior(AMove(unit, target))




        #for Unit in main_attack_force:
        #    main_maneuver = CombatManeuver()
        #    main_maneuver.add(AttackTarget(Unit, target))
            #main_maneuver.add(AMove(unit=Unit, target=target))
            #self.register_behavior(AMove(unit, self.game_info.map_center))


        # step logic here ...
        pass


#_______________________________________________________________________________________________________________________
#          ON UNIT CREATED
#_______________________________________________________________________________________________________________________



    async def on_unit_created(self, unit: Unit) -> None:
        await super(MyBot, self).on_unit_created(unit)

        if unit.type_id == UnitTypeId.ROACH:
            print("roach")

        if unit.type_id == UnitTypeId.ZERGLING:
            print("zergling")


        # assign all units to ATTACKING_MAIN_SQUAD role by default
        if unit.type_id in self.ZERG_UNIT_TYPE:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.ATTACKING_MAIN_SQUAD
            )

        # assign all units to ATTACKING_MAIN_SQUAD role by default
        if unit.type_id == UnitTypeId.ZERGLING:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.CONTROL_GROUP_ONE
            )

        # assign all units to ATTACKING_MAIN_SQUAD role by default
        if unit.type_id == UnitTypeId.ROACH:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.CONTROL_GROUP_TWO
            )

        # assign all units to ATTACKING_MAIN_SQUAD role by default
        if unit.type_id == UnitTypeId.QUEEN:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.CONTROL_GROUP_THREE
            )


        # assign all units to ATTACKING_MAIN_SQUAD role by default
        if unit.type_id == UnitTypeId.DRONE:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.CONTROL_GROUP_FOUR
            )

        # assign all units to ATTACKING_MAIN_SQUAD role by default
        if unit.type_id == UnitTypeId.BANELING:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.CONTROL_GROUP_FIVE
            )

        # assign all units to ATTACKING_MAIN_SQUAD role by default
        if unit.type_id == UnitTypeId.RAVAGER:
            self.mediator.assign_role(
                tag=unit.tag, role=UnitRole.CONTROL_GROUP_SIX
            )







#_______________________________________________________________________________________________________________________
#          DEBUG TOOL
#_______________________________________________________________________________________________________________________

    async def debug_tool(self):
        current_time = time.time()
        if current_time - self.last_debug_time >= 1:  # Se passou mais de um segundo
            #print(self.mediator.get_all_enemy)
            #print("Enemy Race: ", self.EnemyRace)
            #print("Second Base: ", self.second_base)
            #print("Enemy Strategy: ", self.enemy_strategy)
            #print("Creep Queens: ", self.creep_queen_tags)
            #print("Creep Queen Policy: ", self.creep_queen_policy)
            #print("RallyPointSet: ", self.rally_point_set)
            #print("Enemy Structures: ", self.enemy_structures)
            print("Enemy Units: ", self.enemy_units)
            print("Unit Roles: ", self.mediator.get_unit_role_dict)
            print("zergling_squad: ", self.zergling_squad)
            #print("FirstBase: ", self.first_base)
            #print("SecondBase: ", self.second_base)
            self.last_debug_time = current_time  # Atualizar a última vez que a ferramenta de debug foi chamada


#_______________________________________________________________________________________________________________________
#          COMBAT MANEUVER
#_______________________________________________________________________________________________________________________


    def zergling_army_attack(self, main_attack_force: Units, attack_target: Point2, ground_grid: np.ndarray) -> None:    
        for unit in main_attack_force:
            if unit.is_idle:  # Verifica se a unidade está ociosa antes de dar o comando
                main_maneuver = CombatManeuver()
                main_maneuver.add(AMove(unit, attack_target))
                self.register_behavior(main_maneuver)
    """
    Can use `python-sc2` hooks as usual, but make a call the inherited method in the superclass
    Examples:
    """
    # async def on_start(self) -> None:
    #     await super(MyBot, self).on_start()
    #
    #     # on_start logic here ...
    #
    # async def on_end(self, game_result: Result) -> None:
    #     await super(MyBot, self).on_end(game_result)
    #
    #     # custom on_end logic here ...
    #
    # async def on_building_construction_complete(self, unit: Unit) -> None:
    #     await super(MyBot, self).on_building_construction_complete(unit)
    #
    #     # custom on_building_construction_complete logic here ...
    #
    # async def on_unit_created(self, unit: Unit) -> None:
    #     await super(MyBot, self).on_unit_created(unit)
    #
    #     # custom on_unit_created logic here ...
    #
    # async def on_unit_destroyed(self, unit_tag: int) -> None:
    #     await super(MyBot, self).on_unit_destroyed(unit_tag)
    #
    #     # custom on_unit_destroyed logic here ...
    #
    # async def on_unit_took_damage(self, unit: Unit, amount_damage_taken: float) -> None:
    #     await super(MyBot, self).on_unit_took_damage(unit, amount_damage_taken)
    #
    #     # custom on_unit_took_damage logic here ...